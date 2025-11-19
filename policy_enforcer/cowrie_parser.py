# policy_enforcer/cowrie_parser.py

import json
import re
from typing import Optional

IPV4_REGEX = re.compile(
    r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
)

def extract_attacker_ip(log_line: str) -> Optional[str]:
    """
    Try to extract an attacker/source IP from a Cowrie log line.
    Handles both JSON logs and plain text as a fallback.
    """
    log_line = log_line.strip()
    if not log_line:
        return None

    # 1) Try JSON format first (Cowrie often logs JSON)
    try:
        data = json.loads(log_line)
        for key in ("src_ip", "peerIP", "src_ip_addr"):
            if key in data:
                return str(data[key])
    except json.JSONDecodeError:
        pass

    # 2) Fallback: regex for any IPv4 in the line
    match = IPV4_REGEX.search(log_line)
    if match:
        return match.group(0)

    return None
