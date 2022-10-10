---
layout: default
title: Intro
description: "Smol K8s Homelab Overview"
nav_order: 1
permalink: /
---

# Smol K8s Homelab
We throw local k8s (kubernetes) testing tools in this repo, mainly [`smol-k8s-lab.py`](./smol-k8s-lab.py). This project is aimed at getting up and running quickly with mostly smaller k8s distros in one small command line script, but there's also full tutorials to manually set up each distro in the [docs we maintain](https://jessebot.github.io/smol_k8s_homelab/distros) as well as BASH scripts for basic automation of each k8s distro in each directory under `./distro/[NAME OF K8S DISTRO]/bash_full_quickstart.sh`.

## QuickStart
Get started with `smol-k8s-lab.py` today with our tutorial [here](https://jessebot.github.io/smol_k8s_homelab/quickstart).

### Currently supported k8s distros

| Distro | [smol-k8s-lab.py](./smol-k8s-lab.py) Support |
|:------:|:--------------------------------------------:|
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/k3s_icon.ico" width="32">[k3s](https://k3s.io/)            | ✅ | 
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/kind_icon.png" width="32">[KinD](https://kind.sigs.k8s.io/) | ✅ | 

### Stack We Install on K8s
We tend to test first on k3s and then kind.

| Application/Tool | What is it? |
|:----------------:|:------------|
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/metallb_icon.png" width="32"> [metallb](https://github.io/metallb/metallb) | loadbalancer for metal, since we're mostly selfhosting |
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/nginx.ico" width="32"> [nginx-ingress-controller](https://github.io/kubernetes/ingress-nginx) | Ingress allows access to the cluster remotely, needed for web traffic |
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/cert-manager.png" width="32"> [cert-manager](https://cert-manager.io/docs/) | For SSL/TLS certificates |
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/k9s_icon.png" width="32"> [k9s](https://k9scli.io/topics/install/) | Terminal based dashboard for kubernetes |
| [Local Path Provisioner](https://github.com/rancher/local-path-provisioner) | Default simple local file storage for persistent data |


#### Optionally installed

| Application/Tool | What is it? |
|:---:|:---| 
| [sealed-secrets](https://github.com/bitnami-labs/sealed-secrets) | Encrypts secrets files so you can check them into git |
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/eso_icon.png" width="32"> [external-secrets-operator](https://external-secrets.io/v0.5.9/) | integrates external secret management systems like GitLab|
| <img src="https://raw.githubusercontent.com/jessebot/smol_k8s_homelab/main/icons/argo_icon.png" width="32">[argo-cd](https://github.io/argoproj/argo-helm) | Gitops - Continuous Deployment |

If you install argocd, and you use bitwarden, we'll generate an admin password and automatically place it in your vault if you pass in the `-p` option. Curently only works with Bitwarden.

Want to get started with argocd? If you've installed it via smol_k8s_homelab, then you can jump [here](https://github.com/jessebot/argo-example#argo-via-the-gui). Otherwise, if you want to start from scratch, start [here](https://github.com/jessebot/argo-example#argocd)


### Port Forwarding
If you want to access an app outside of port forwarding to test, you'll need to make sure your app's ingress is setup correctly and then you'll need to setup your router to port forward 80->80 and 443->443 for your WAN. then setup DNS for your domain if you want the wider internet to access this remotely.

### SSL/TLS

After SSL is working (if it's not, follow the steps in the [cert-manager common error troubleshooting guide](https://cert-manager.io/docs/faq/acme/#common-errors)), you can also change the `letsencrypt-staging` value to `letsencrypt-prod` for any domains you own and can configure to point to your cluster via DNS.

### Troubleshooting
If you're stuck, checkout the [Troubleshooting section](https://jessebot.github.io/smol_k8s_homelab/troubleshooting) to see if we also got stuck on the same thing at some point :)
