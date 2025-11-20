#!/usr/bin/env bash
set -euo pipefail

echo "[*] Applying namespaces..."
kubectl apply -f k8s/namespaces/honeypots-namespace.yaml
kubectl apply -f k8s/namespaces/app-namespace.yaml
kubectl apply -f k8s/namespaces/security-namespace.yaml

echo "[*] Installing Calico (if not already installed)..."
kubectl apply -f k8s/calico/calico-install.yaml

echo "[*] Deploying honeypots..."
kubectl apply -f k8s/honeypots/dummy-honeypot.yaml
kubectl apply -f k8s/honeypots/cowrie.yaml

echo "[*] Deploying application (frontend + backend)..."
kubectl apply -f k8s/app/frontend-backend.yaml

echo "[*] Applying network policies..."
kubectl apply -f k8s/network-policies/honeypots-default-deny.yaml || true
kubectl apply -f k8s/network-policies/block-dummy-nginx.yaml
kubectl apply -f k8s/network-policies/app-default-deny.yaml
kubectl apply -f k8s/network-policies/app-allow-frontend-to-backend.yaml

echo "[*] Applying security (policy enforcer RBAC + deployment)..."
kubectl apply -f k8s/security/policy-enforcer.yaml

echo "[+] Done. Current pods:"
kubectl get pods -A
