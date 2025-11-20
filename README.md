# Dynamic Policy Honeypot System (Kubernetes + Calico)

This project implements a **cloud-native dynamic honeypot system** on top of Kubernetes.  
Honeypots (e.g., Cowrie) lure attackers, and a custom **Policy Enforcer** automatically updates
**Calico** network policies to block malicious IPs in real time.

> Honeypot → Detect attacker → Adaptive policy update → Attacker gets isolated.

---

## ✨ Features

- 🪤 **Honeypots on Kubernetes**
  - Cowrie SSH honeypot
  - Dummy HTTP honeypot (nginx) for testing policies
  - (Planned) Custom Python honeypot (`PyTrap`) for richer interaction logging

- 🔐 **Microsegmentation with Calico**
  - Separate namespaces: `honeypots`, `app`, `security`
  - Default-deny ingress policies
  - Explicit allow: `app-frontend` → `app-backend`
  - Isolation between normal app traffic and honeypots

- 🤖 **Adaptive Policy Enforcer (Python)**
  - Streams Cowrie logs via Kubernetes API
  - Extracts attacker IPs from logs
  - Updates a Calico `GlobalNetworkPolicy` to deny traffic from those IPs
  - Works on any Calico-enabled Kubernetes cluster

- ☁️ **Cloud-ready design**
  - Developed on k3s + Calico in a VM
  - Manifests are portable to cloud clusters (EKS/AKS/etc.)
  - Optional NodePort / LoadBalancer exposure for external attacker traffic

---

## 🧭 Operations Guide

For details on how to start/stop the VM, restart k3s, and keep the system running smoothly, see:

➡️ [Operational Tips & Running Smoothly](docs/running-smoothly.md)

---

## 🧱 High-Level Architecture

Namespaces:

- `honeypots` — Cowrie + dummy nginx honeypot
- `app` — simple frontend/backend application
- `security` — Policy Enforcer and RBAC

Data flow:

1. **Attacker** connects to honeypot Service.
2. **Cowrie** logs the interaction (source IP, commands, etc.).
3. **Policy Enforcer** (Python) tails honeypot logs via Kubernetes API.
4. When a new attacker IP is seen, the enforcer:
   - updates a Calico `GlobalNetworkPolicy` (`block-attacker-ips`)
   - adds the attacker IP as a `/32` entry in the `nets` list.
5. Calico enforces the policy; subsequent connections from that IP are **denied**.

---

## 📂 Repository Structure

```text
k8s/
  calico/
    calico-policy-only.yaml           # Calico CNI / policy engine

  namespaces/
    honeypots-namespace.yaml      # Namespace for honeypots
    app-namespace.yaml            # Namespace for demo app
    security-namespace.yaml       # Namespace for policy enforcer

  honeypots/
    cowrie.yaml                   # Cowrie SSH honeypot deployment + service
    dummy-honeypot.yaml           # Simple nginx honeypot for testing

  app/
    frontend-backend.yaml         # Demo app: frontend + backend + service

  network-policies/
    honeypots-default-deny.yaml   # (Optional) Default-deny for honeypots
    block-dummy-nginx.yaml        # Deny all ingress to dummy honeypot
    app-default-deny.yaml         # Default-deny for `app` namespace
    app-allow-frontend-to-backend.yaml # Allow only frontend → backend

  security/
    policy-enforcer.yaml          # Namespace, SA, RBAC, Deployment for enforcer (optional)

policy_enforcer/
  main.py                         # Main event loop (log watcher + policy updater)
  cowrie_parser.py                # Extract attacker IP from Cowrie log lines
  calico_client.py                # Create/update Calico GlobalNetworkPolicy

scripts/
  deploy-all.sh                   # Apply everything in the correct order
  teardown-all.sh                 # Clean teardown of demo resources

requirements.txt                  # Python dependencies
README.md
