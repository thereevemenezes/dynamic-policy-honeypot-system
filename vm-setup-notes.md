# Netsec Lab – VM Setup Notes

## 1. VM Specs (VirtualBox)

- Name: `netsec-lab`
- Type: Linux
- Version: Ubuntu (64-bit)
- RAM: **2048 MB**
- CPU: **2 cores**
- Disk: **20 GB**, VDI, dynamically allocated
- OS ISO: **Ubuntu Server 22.04 LTS**

During install:

- Chose **Ubuntu Server**
- Used entire disk (default partitioning)
- Enabled **OpenSSH server**
- Created user: `reeve` (or whatever you used)

---

## 2. Initial Ubuntu Setup

````bash
# Update and upgrade packages
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install git -y

# Configure your identity for commits
git config --global user.name "Clifford Reeve Menezes"
git config --global user.email "your-github-email@example.com"

# Update package index
sudo apt update

# Install Docker from Ubuntu repos
sudo apt install docker.io -y

# Add current user to docker group (so we don't need sudo)
sudo usermod -aG docker $USER

# Apply new group without logging out
newgrp docker

# Test Docker
docker ps   # should show an empty table, no errors


That’s it for what you’ve done so far ✅

You can also keep another section ready for the *next steps*:

```md
## 5. Install k3s (Kubernetes) – TO DO

```bash
curl -sfL https://get.k3s.io | sh -
# ... (rest to be filled later)

# Install k3s
curl -sfL https://get.k3s.io | sh -

# Fix kubeconfig permissions
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Check cluster
kubectl get nodes
kubectl get pods -A




````
