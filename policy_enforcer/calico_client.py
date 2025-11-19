# policy_enforcer/calico_client.py

from typing import Set, Dict, Any, List

from kubernetes import client
from kubernetes.client import ApiException

CALICO_GROUP = "crd.projectcalico.org"
CALICO_VERSION = "v1"
CALICO_GNP_PLURAL = "globalnetworkpolicies"

BLOCK_POLICY_NAME = "block-attacker-ips"


def _default_block_policy_body() -> Dict[str, Any]:
    """
    Return a default GlobalNetworkPolicy spec that denies ingress
    from a list of source IPs (nets).
    """
    return {
        "apiVersion": f"{CALICO_GROUP}/{CALICO_VERSION}",
        "kind": "GlobalNetworkPolicy",
        "metadata": {
            "name": BLOCK_POLICY_NAME,
        },
        "spec": {
            "order": 100,
            "selector": "all()",        # apply to all endpoints; you can tighten this later
            "types": ["Ingress"],
            "ingress": [
                {
                    "action": "Deny",
                    "source": {
                        "nets": []      # we'll populate with x.x.x.x/32 entries
                    }
                }
            ],
        },
    }


def ensure_block_policy(custom_api: client.CustomObjectsApi) -> Dict[str, Any]:
    """
    Ensure the GlobalNetworkPolicy for blocking attacker IPs exists.
    Returns the current policy object.
    """
    try:
        gnp = custom_api.get_cluster_custom_object(
            group=CALICO_GROUP,
            version=CALICO_VERSION,
            plural=CALICO_GNP_PLURAL,
            name=BLOCK_POLICY_NAME,
        )
        return gnp
    except ApiException as e:
        if e.status != 404:
            raise
        # Create it if it doesn't exist
        body = _default_block_policy_body()
        return custom_api.create_cluster_custom_object(
            group=CALICO_GROUP,
            version=CALICO_VERSION,
            plural=CALICO_GNP_PLURAL,
            body=body,
        )


def get_blocked_ips_from_policy(gnp: Dict[str, Any]) -> Set[str]:
    """
    Read the currently blocked IPs (as /32 nets) from the policy.
    Returns a set of plain IP strings like '1.2.3.4'.
    """
    blocked: Set[str] = set()

    try:
        ingress: List[Dict[str, Any]] = gnp["spec"]["ingress"]
        if not ingress:
            return blocked
        rule = ingress[0]
        nets: List[str] = rule.get("source", {}).get("nets", [])
        for net in nets:
            if net.endswith("/32"):
                blocked.add(net[:-3])
            else:
                blocked.add(net)
    except (KeyError, TypeError):
        pass

    return blocked


def add_blocked_ip(
    custom_api: client.CustomObjectsApi,
    current_policy: Dict[str, Any],
    new_ip: str,
) -> Dict[str, Any]:
    """
    Add a new IP to the GlobalNetworkPolicy nets[] list (as x.x.x.x/32).
    Returns the updated policy object.
    """
    nets = []
    try:
        ingress = current_policy["spec"]["ingress"]
        rule = ingress[0]
        nets = rule.setdefault("source", {}).setdefault("nets", [])
    except (KeyError, IndexError, TypeError):
        # if structure missing, reset to default and then use that
        current_policy = _default_block_policy_body()
        nets = current_policy["spec"]["ingress"][0]["source"]["nets"]

    candidate = f"{new_ip}/32"
    if candidate not in nets:
        nets.append(candidate)

    # Replace the cluster-scoped CRD
    updated = custom_api.replace_cluster_custom_object(
        group=CALICO_GROUP,
        version=CALICO_VERSION,
        plural=CALICO_GNP_PLURAL,
        name=BLOCK_POLICY_NAME,
        body=current_policy,
    )
    return updated
