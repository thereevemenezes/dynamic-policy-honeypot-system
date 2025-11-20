#!/usr/bin/env bash
set -euo pipefail

echo "[*] Deleting security components..."
kubectl delete -f k8s/security/policy-enforcer.yaml --ignore-not-found=true

echo "[*] Deleting app components..."
kubectl delete -f k8s/app/frontend-backend.yaml --ignore-not-found=true

echo "[*] Deleting honeypots..."
kubectl delete -f k8s/honeypots/cowrie.yaml --ignore-not-found=true
kubectl delete -f k8s/honeypots/dummy-honeypot.yaml --ignore-not-found=true

echo "[*] Deleting network policies..."
kubectl delete -f k8s/network-policies/app-allow-frontend-to-backend.yaml --ignore-not-found=true
kubectl delete -f k8s/network-policies/app-default-deny.yaml --ignore-not-found=true
kubectl delete -f k8s/network-policies/block-dummy-nginx.yaml --ignore-not-found=true
kubectl delete -f k8s/network-policies/honeypots-default-deny.yaml --ignore-not-found=true

echo "[*] Deleting namespaces..."
kubectl delete -f k8s/namespaces/security-namespace.yaml --ignore-not-found=true
kubectl delete -f k8s/namespaces/app-namespace.yaml --ignore-not-found=true
kubectl delete -f k8s/namespaces/honeypots-namespace.yaml --ignore-not-found=true

echo "[+] Teardown complete."
