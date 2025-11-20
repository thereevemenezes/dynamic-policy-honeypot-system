#!/usr/bin/env bash
set -euo pipefail

echo "[*] Starting k3s..."
sudo systemctl start k3s

echo "[*] Waiting a few seconds for API server..."
sleep 10

echo "[*] Exporting kubeconfig..."
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo "[*] Checking cluster health..."
kubectl get nodes
kubectl get pods -A

echo "[+] Cluster looks healthy. If you want to (re)deploy everything, run:"
echo "    ./scripts/deploy-all.sh"
