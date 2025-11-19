# policy_enforcer/main.py

import time
from typing import Set

from kubernetes import client, config
from kubernetes.client import ApiException

from policy_enforcer.cowrie_parser import extract_attacker_ip
from policy_enforcer.calico_client import (
    ensure_block_policy,
    get_blocked_ips_from_policy,
    add_blocked_ip,
)


HONEYPOTS_NAMESPACE = "honeypots"
HONEYPOT_LABEL_SELECTOR = "app=cowrie-honeypot"


def load_kube_config():
    """
    Try in-cluster config first (for when we run inside Kubernetes),
    then fall back to local kubeconfig (for running from VM directly).
    """
    try:
        config.load_incluster_config()
        print("[*] Loaded in-cluster Kubernetes config")
    except config.ConfigException:
        config.load_kube_config()
        print("[*] Loaded local kubeconfig")


def stream_cowrie_logs(core_api: client.CoreV1Api):
    """
    Simple log streamer: attach to the first Cowrie pod and stream its logs.
    Later you can extend this to handle multiple pods or restart logic.
    """
    pods = core_api.list_namespaced_pod(
        namespace=HONEYPOTS_NAMESPACE,
        label_selector=HONEYPOT_LABEL_SELECTOR,
    ).items

    if not pods:
        print("[!] No Cowrie pods found, sleeping and retrying...")
        time.sleep(5)
        return

    pod_name = pods[0].metadata.name
    print(f"[*] Streaming logs from pod: {pod_name}")

    # follow=True + _preload_content=False gives us a streaming response
    resp = core_api.read_namespaced_pod_log(
        name=pod_name,
        namespace=HONEYPOTS_NAMESPACE,
        follow=True,
        tail_lines=10,
        _preload_content=False,
    )

    try:
        for line in resp:
            if not line:
                continue
            yield line.decode("utf-8", errors="ignore")
    finally:
        resp.close()


def main():
    load_kube_config()

    core_api = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()

    # Ensure we have a global block policy
    gnp = ensure_block_policy(custom_api)
    blocked_ips: Set[str] = get_blocked_ips_from_policy(gnp)
    print(f"[*] Existing blocked IPs: {blocked_ips}")

    while True:
        try:
            for log_line in stream_cowrie_logs(core_api):
                ip = extract_attacker_ip(log_line)
                if not ip:
                    continue

                if ip in blocked_ips:
                    # Already blocked
                    continue

                print(f"[+] New attacker IP detected: {ip}")
                try:
                    gnp = add_blocked_ip(custom_api, gnp, ip)
                    blocked_ips.add(ip)
                    print(f"[+] Added {ip} to GlobalNetworkPolicy {gnp['metadata']['name']}")
                except ApiException as e:
                    print(f"[!] Failed to update GlobalNetworkPolicy: {e}")
        except Exception as e:
            print(f"[!] Error in log streaming loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
