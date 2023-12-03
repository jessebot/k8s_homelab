<h1 align="center">
🧸 Smol K8s Lab </h1>

<p align="center">
Smol K8s Lab leverages Argo CD and slim k8s distributions like K3s to create production-like environments via a declarative workflow. Batteries and 🦑 included.</i>
</p>
<p align="center">
  <a href="https://github.com/jessebot/smol-k8s-lab/releases">
    <img src="https://img.shields.io/github/v/release/jessebot/smol-k8s-lab?style=plastic&labelColor=484848&color=3CA324&logo=GitHub&logoColor=white">
  </a>
</p>
<p align="center">
  <a href="images/screenshots/help_text.svg">
      <img src="images/screenshots/help_text.svg" alt="Output of smol-k8s-lab --help after cloning the directory and installing the prerequisites.">
  </a>
</p>

## About

`smol-k8s-lab`'s declarative workflow enables rapid iteration in production-like environments with minimal costs for failure. This makes it ideal for proof-of-concepts, prototyping, and benchmarking Kubernetes applications and distributions! 💙

By default, `smol-k8s-lab` deploys [Argo CD] + [Argo CD Appset Secret Plugin] which enables Argo CD to securely manage your lab via files in open-source Git repos. Additionally, a customized dark-theme is provided for Argo CD's incredibly useful web-interface.

## Installation

Please see [our installation guide](/installation)

## Usage

After you've followed the installation instructions, if you're *new* to `smol-k8s-lab`,  initialize a new config file by running:

```bash
# we'll walk you through any configuration needed
# before saving the config and deploying it for you
smol-k8s-lab
```

### Adding custom Applications

You can create any application you already have an Argo CD application repo for, by following a simple application yaml schema in `~/.config/smol-k8s-lab/config.yaml` like this:

```yaml
apps:
  # name of application to create in Argo CD
  cert_manager:
    # if set to false, we ignore this app
    enabled: true
    argo:
      # secret keys to pass to Argo CD Application Set Generator
      secret_keys:
        # Used for letsencrypt-staging, to generate certs. If set to "" and cert-manager.enabled is true
        # smol-k8s-lab will prompt for this value and save it back to this file for you.
        email: ""
      # If set to "", we'll instead use the repo, path, ref, namespace, and project_source_repos
      # git repo to install the Argo CD app from
      repo: "https://github.com/small-hack/argocd-apps"
      # path in the argo repo to point to. Trailing slash very important!
      path: "ingress/cert-manager/"
      # either the branch or tag to point at in the argo repo above
      ref: "main"
      # namespace to install the k8s app in
      namespace: "ingress"
      # source repos for cert-manager CD App Project (in addition to cert-manager.argo.repo)
      project_source_repos:
        - https://charts.jetstack.io
```

Note: the above application, cert-manager, is already included as a default application in smol-k8s-lab :)

# Under the hood
Note: this project is not officially affiliated with any of the below tooling or applications.


## Supported k8s distributions
We always install the latest version of Kubernetes that is available from the distro's startup script.

|  Distro    |         Description              |
|:----------:|:------------------------------------------------------|
| [<img src="images/icons/k3s_icon.ico" width="26">][k3s] <br /> [k3s] | The certified Kubernetes distribution built for IoT & Edge computing |
| [<img src="images/icons/k3d.png" width="26">][k3d] <br /> [k3d] | K3d is k3s in Docker 🐳. <br> ⚠️ testing |
| [<img src="images/icons/kind_icon.png" width="32">][KinD] <br /> [KinD] | kind is a tool for running local Kubernetes clusters using Docker container “nodes”. kind was primarily designed for testing Kubernetes itself, but may be used for local development or CI. |

We tend to test first on k3s first, then the other distros. k3d support coming soon.

## Default Installed Applications
Version is the helm chart version, or manifest version.

|           Application           |                      Description                      | Initialization Supported |
|:-------------------------------:|:------------------------------------------------------|:------------------------:|
| [<img src="images/icons/metallb_icon.png" width="32px" alt="metallb logo, blue arrow pointing up, with small line on one leg of arrow to show balance">][metallb] <br /> [metallb] | Loadbalancer and IP Address pool manager for metal | ✅ |
| [<img src="images/icons/nginx.ico" width="32px" alt="nginx logo, white letter N with green background">][ingress-nginx] <br /> [ingress-nginx] | The ingress-nginx controller allows access to the cluster remotely, needed for web traffic | ❌ |
| [<img src="images/icons/cert-manager_icon.png" width="32px" alt="cert manager logo">][cert-manager] <br /> [cert-manager] | For SSL/TLS certificates | ✅ |
| [<img src="images/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD] <br /> [Argo CD] | Gitops - Continuous Deployment | ✅ |
| [<img src="images/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD Appset Secret Plugin] <br /> [Argo CD Appset Secret Plugin] | Gitops - Continuous Deployment | ✅ |
| [<img src="images/icons/eso_icon.png" width="32" alt="ESO logo, outline of robot with astricks in a screen in it's belly">][ESO] <br /> [ESO] | external-secrets-operator integrates external secret management systems like Bitwarden or GitLab | ❌ |
| [<img src="images/icons/eso_icon.png" width="32" alt="ESO logo, again">][Bitwarden ESO Provider] <br /> [Bitwarden ESO Provider] | Bitwarden external-secrets-operator provider  | ✅ |
| [<img src="images/icons/zitadel.png" width="32" alt="Zitadel logo, an orange arrow pointing left">][ZITADEL] <br /> [ZITADEL] | An identity provider and OIDC provider to provide SSO | ✅ |
| [<img src="images/icons/vouch.png" width="32" alt="Vouch logo, the letter V in rainbow ">][Vouch] <br /> [Vouch] | Vouch proxy allows you to secure web pages that lack authentication e.g. prometheus | ✅ |
| [<img src="images/icons/prometheus.png" width="32" alt="Prometheus logo, a torch">][Prometheus Stack] <br /> [Prometheus Stack] | Prometheus monitoring and logging stack using [loki]/[promtail], [alert manager], and [grafana]  | ✅ |


Minor Notes:

>All Default Applications can be disabled through your `~/.config/smol-k8s-lab/config.yaml` file, **except**:</sub>
>
>    - ingress-nginx is the currently the only _supported_ ingress-controller. traefik support is being worked on.</sub>
>
>    - Argo CD is optional, but if not installed, smol-k8s-lab will <i>only</i> install: metallb, nginx-ingress, and cert-manager</sub>


## Optionally Installed Applications

| Application/Tool | Description | Initialization Supported |
|:----------------:|:------------|:------------------------:|
| [<img src="images/icons/cilium.png"  width="32" alt="cilium logo">][Cilium] <br /> [Cilium]<sup>alpha</sup> | Kubernetes netflow visualizer and policy editor | ✅ |
| [<img src="images/icons/kyverno_icon.png"  width="32" alt="kyvero logo">][Kyverno] <br /> [Kyverno]<sup>alpha</sup> | Kubernetes native policy management to enforce policies on k8s resources | ❌ |
| [<img src="images/icons/kepler.png" width="32" alt="kepler logo">][kepler] <br /> [kepler] | Kepler (Kubernetes Efficient Power Level Exporter) uses eBPF to probe energy-related system stats and exports them as Prometheus metrics. | ✅ |
| [<img src="images/icons/k8up.png" width="32" alt="k8up logo, a minimalist logo of a small blue hill with line starting the right going into the hill">][k8up] <br /> [k8up] | Backups operator using [restic] to backup to s3 endpoints | ✅ |
| [<img src="images/icons/k8tz.png" width="32" alt="k8tz logo, the k8s logo but with a watch in the center instead of the ship wheel">][k8tz] <br /> [k8tz] | Timezone environment variable injector for pods and cronjobs | ✅ |
| [<img src="images/icons/nextcloud.png" width="32" alt="nextcloud logo, 3 white circles touching eachother on a blue background">][Nextcloud] <br /> [Nextcloud] | Nextcloud is a self hosted file server | ✅ |
| [<img src="images/icons/mastodon.png" width="32" alt="Mastodon logo, a white M in a purple chat bubble">][Mastodon] <br /> [Mastodon] | Mastodon is a self hosted federated social media network  | ✅ |
| [<img src="images/icons/matrix.png" width="32" alt="Matrix logo">][matrix] <br /> [matrix] | Matrix is a self hosted chat platform  | ✅ |
| [<img src="images/icons/minio.png" width="32" alt="minio logo, a minimalist drawing in red of a crane">][minio] <br /> [minio] | Self hosted S3 Object Store operator | ✅ |
| [<img src="images/icons/seaweedfs.png" width="32" alt="seaweedfs logo, ">][seaweedfs] <br /> [seaweedfs] | Self hosted S3 Object Store | ✅ |
| [<img src="images/icons/k9s_icon.png" alt="k9s logo, outline of dog with ship wheels for eyes" width="32px">][k9s]</br>[k9s] | Terminal based dashboard for kubernetes | ✅ |


## Troubleshooting
If you're stuck, checkout the [Notes](https://jessebot.github.io/smol-k8s-lab/notes) to see if we also got stuck on the same thing at some point :) Under each Kubernetes distro or application, we'll have notes on how to learn more about it, as well as any errors we've already battled.


# Status
This is still in early beta, as we figure out all the apps and distros we want to support, and pin all the versions, but if you'd like to contribute or just found a :bug:, feel free to open an issue (or pull request), and we'll take a look! We'll try to get back to you asap!


## Development
smol-k8s-lab is written in Python and built and published using [Poetry]. You can check out the `pyproject.toml` for the versions of each library we install below:

- [bcrypt] (to pass a password to argocd and automatically update your Bitwarden)
- [rich] (this is what makes all the pretty formatted text in logs and `--help`)
- [textual] (this is the framework used for writing the TUI)
- [ruamel.yaml] (to handle the k8s yamls and configs while maintaining comments)
- [click] (handles arguments for the CLI)

We also utilize the [Bitwarden cli], for a password manager so you never have to see/know your Argo CD password.

## Things we don't handle (yet)

1. Port Forwarding

    If you want to access an app outside of port forwarding to test, you'll need to make sure your app's ingress is setup correctly and then you'll need to setup your router to port forward 80->80 and 443->443 for your WAN. Then, setup DNS for your domain if you want the wider internet to access this remotely.

2. High-Availability

    HA cluster design with K3s requires etcd or another external key-value store such as PostgreSQL. Smol-K8s-Lab deploys k3s in a single-node configuration using SQLite which can be used for multi-node configurations but is not suitable for high-availability.

### Troubleshooting

If you're stuck, checkout the [Notes section](https://jessebot.github.io/smol-k8s-lab/notes) to see if we also got stuck on the same thing at some point :)

<!-- k8s apps link references -->
[Local Path Provisioner]: https://github.com/rancher/local-path-provisioner
[nginx-ingress]: https://github.io/kubernetes/ingress-nginx

<!-- k8s distro link references -->
[k3s]: https://k3s.io/
[k3d]: https://k3d.io/
[KinD]: https://kind.sigs.k8s.io/

<!-- k8s optional apps link references -->
[ESO]: https://external-secrets.io
[alert manager]: https://prometheus.io/docs/alerting/latest/alertmanager/
[Argo CD]:https://argo-cd.readthedocs.io/en/latest/
[Argo CD Appset Secret Plugin]: https://github.com/small-hack/argocd-appset-secret-plugin/

[cert-manager]: https://cert-manager.io/docs/
[cilium]: https://github.com/cilium/cilium/tree/v1.14.1/install/kubernetes/cilium
[Bitwarden ESO Provider]: https://github.com/jessebot/bitwarden-eso-provider
[grafana]: https://grafana.com/
[ingress-nginx]: https://github.io/kubernetes/ingress-nginx
[k8tz]: https://github.com/small-hack/argocd-apps/tree/main/alpha/k8tz
[k8up]: https://k8up.io
[Kyverno]: https://github.com/kyverno/kyverno/
[kepler]: https://github.com/sustainable-computing-io/kepler-helm-chart/tree/main/chart/kepler
[Local Path Provisioner]: https://github.com/rancher/local-path-provisioner
[loki]: https://grafana.com/oss/loki/
[Mastodon]: https://joinmastodon.org/
[matrix]: https://matrix.org/
[metallb]: https://github.io/metallb/metallb "metallb"
[minio]: https://min.io/
[Nextcloud]: https://github.com/nextcloud/helm
[Prometheus Stack]: https://github.com/small-hack/argocd-apps/tree/main/prometheus
[promtail]: https://grafana.com/docs/loki/latest/send-data/promtail/
[seaweedfs]: https://github.com/seaweedfs/seaweedfs
[Vouch]: https://github.com/jessebot/vouch-helm-chart
[ZITADEL]: https://github.com/zitadel/zitadel-charts/tree/main

<!-- k8s tooling reference -->
[`brew`]: https://brew.sh
[k9s]: https://k9scli.io/topics/install/
[restic]: https://restic.readthedocs.io/en/stable/

<!-- smol-k8s-lab dependency lib link references -->
[Poetry]: https://python-poetry.org/
[rich]: https://github.com/Textualize/richP
[textual]: https://github.com/Textualize/textual
[PyYAML]: https://pyyaml.org/
[bcrypt]: https://pypi.org/project/bcrypt/
[click]: https://pypi.org/project/click/
[Bitwarden cli]: https://bitwarden.com/help/cli/
