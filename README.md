<h2 align="center">
  <img
    src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png"
    height="30"
    width="0px"
  />
smol k8s lab 🧸 <sub>Now with more :squid:</sub>
</h2>

<p align="center">
  <a href="https://github.com/jessebot/smol-k8s-lab/releases">
    <img src="https://img.shields.io/github/v/release/jessebot/smol-k8s-lab?style=plastic&labelColor=484848&color=3CA324&logo=GitHub&logoColor=white">
  </a>
</p>

A tool to run slimmer k8s distros on metal, with batteries included. Deploys Argo CD by default, so you can mange your entire local testing lab from the very beginning using files in [open source git repos](), and with the help of a very handy dashboard.

Also helpful for benchmarking various [k8s distros](#supported-k8s-distributions)! 💙


<p align="center">
  <a href="https://raw.githubusercontent.com/jessebot/smol-k8s-lab/main/docs/screenshots/help_text.svg">
      <img src="./docs/screenshots/help_text.svg" alt="Output of smol-k8s-lab --help after cloning the directory and installing the prerequisites.">
  </a>
</p>


## Getting Started

### Installation
smol-k8s-lab requires Python 3.11. If you've already got it and [`brew`] installed, you should be able to:

```bash
# install the CLI
pip3.11 install smol-k8s-lab

# Check the help menu before proceeding
smol-k8s-lab --help
```

### Configuration
We've got a [Quickstart guide](https://small-hack.github.io/smol-k8s-lab/quickstart) for you to jump right in :)

## Under the hood
Note: this project is not officially afilliated with any of the below tooling or applications.

### Supported k8s distributions
We always install the latest version of kubernetes that is available from the distro's startup script.

|  Distro    |         Description              |
|:----------:|:------------------------------------------------------|
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k0s-logo.svg" width="32">][k0s] <br /> [k0s] | Simple, Solid & Certified Kubernetes Distribution |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k3s_icon.ico" width="26">][k3s] <br /> [k3s] | The certified Kubernetes distribution built for IoT & Edge computing |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k3s_icon.ico" width="26">][k3d] <br /> [k3d] | **ALPHA - TESTING PHASE** k3s in docker 🐳 |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/kind_icon.png" width="32">][KinD] <br /> [KinD] | kind is a tool for running local Kubernetes clusters using Docker container “nodes”. kind was primarily designed for testing Kubernetes itself, but may be used for local development or CI. |

We tend to test first on k3s first, then the other distros. k3d support coming soon.

### Default Installed Applications
Version is the helm chart version, or manifest version.

|           Application           |                      Description                      | Initialization Supported |
|:-------------------------------:|:------------------------------------------------------|:------------------------:|
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/metallb_icon.png" width="32px" alt="metallb logo, blue arrow pointing up, with small line on one leg of arrow to show balance">][metallb] <br /> [metallb] | Loadbalancer and IP Address pool manager for metal | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/nginx.ico" width="32px" alt="nginx logo, white letter N with green background">][nginx-ingress] <br /> [nginx-ingress] | The ingress controller allows access to the cluster remotely, needed for web traffic | No |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/cert-manager_icon.png" width="32px" alt="cert manager logo">][cert-manager] <br /> [cert-manager] | For SSL/TLS certificates | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD] <br /> [Argo CD] | Gitops - Continuous Deployment | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD Appset Secret Plugin] <br /> [Argo CD Appset Secret Plugin] | Gitops - Continuous Deployment | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/eso_icon.png" width="32" alt="ESO logo, outline of robot with astricks in a screen in it's belly">][ESO] <br /> [ESO] | external-secrets-operator integrates external secret management systems like Bitwarden or GitLab | No |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/bitwarden_icon.png" width="32" alt="Bitwarden logo, ">][Bitwarden ESO Provider] <br /> [Bitwarden ESO Provider] | Bitwarden external-secrets-operator provider  | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/zitadel.png" width="32" alt="Zitadel logo, ">][Zitadel] <br /> [Zitadel] | An identity provider and OIDC provider to provide SSO | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/vouch.png" width="32" alt="Vouch logo, ">][Vouch] <br /> [Vouch] | Vouch proxy allows you to secure web pages that lack authentication e.g. prometheus | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/prometheus.png" width="32" alt="Prometheus logo, ">][Prometheus Stack] <br /> [Prometheus Stack] | Prometheus monitoring and logging stack using [loki]/[promtail], [alert manager], and [grafana]  | Yes |


<sup>**Minor Notes**</sup>
<sub>All Default Applications can be disabled through your `~/.config/smol-k8s-lab/config.yaml` file, **except**:</sub>
<sub>1. nginx-ingress is the currently the only supported ingress-controller. traefik support is being worked on.</sub>
<sub>2. Argo CD is optional, but if not installed, smol-k8s-lab will <i>only</i> install: metallb, nginx-ingress, and cert-manager</sub>

<sub><i>None of these applications are supported or endorsed by their companies/organizations. These are all community maintained Argo CD Application manifests.</i></sub>


### Optionally Installed Applications

| Application/Tool | Description | Initialization Supported |
|:----------------:|:------------|:------------------------:|
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/cilium.png"  width="32" alt="cilium logo">][Cilium] <br /> [Cilium]<sup>alpha</sup> | latest | Kubernetes netflow visualizer and policy editor | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/kyverno_icon.png"  width="32" alt="kyvero logo">][Kyverno] <br /> [Kyverno]<sup>alpha</sup> | latest | Kubernetes native policy management to enforce policies on k8s resources | No |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/keycloak_icon.png"  width="32" alt="keycloak logo">][Keycloak] <br /> [KeyCloak]<sup>alpha</sup> | Self hosted IAM/Oauth2 solution | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/minio.png" width="32" alt="kepler logo, ">][kepler] <br /> [kepler] | Kepler (Kubernetes Efficient Power Level Exporter) uses eBPF to probe energy-related system stats and exports them as Prometheus metrics. | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k8up.png" width="32" alt="k8up logo, ">][k8up] <br /> [k8up] | Backups operator using [restic] to backup to s3 endpoints | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k8tz.png" width="32" alt=" logo, ">][k8tz] <br /> [k8tz] | Timezone environment variable injector for pods and cronjobs | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/nextcloud.png" width="32" alt="nextcloud logo, ">][Nextcloud] <br /> [Nextcloud] | Nextcloud is a self hosted file server | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/mastodon.png" width="32" alt="Mastodon logo, ">][Mastodon] <br /> [Mastodon] | Mastodon is a self hosted federated social media network  | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/matrix.png" width="32" alt="Matrix logo, ">][matrix] <br /> [matrix] | Matrix is a self hosted chat platform  | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/minio.png" width="32" alt="minio logo, ">][minio] <br /> [minio] | Self hosted S3 Object Store operator | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/icons/k9s_icon.png" alt="k9s logo, outline of dog with ship wheels for eyes" width="32px">][k9s]</br>[k9s] | Terminal based dashboard for kubernetes |


## Troubleshooting
If you're stuck, checkout the [Notes](https://jessebot.github.io/smol-k8s-lab/notes) to see if we also got stuck on the same thing at some point :) Under each kubernetes distro or application, we'll have notes on how to learn more about it, as well as any errors we've already battled.


# Status
This is still in later alpha, as we figure out all the apps and distros we want to support, and pin all the versions, but if you'd like to contribute or just found a :bug:, feel free to open an issue (or pull request), and we'll take a look! We'll try to get back to you asap!


### Development
smol-k8s-lab is written in Python and built and published using [Poetry]. You can check out the `pyproject.toml` for the versions of each library we install below:

- [rich] (this is what makes all the pretty formatted text)
- [PyYAML] (to handle the k8s yamls and configs)
- [bcrypt] (to pass a password to argocd and automatically update your Bitwarden)
- [click] (handles arguments for the CLI)

We also utilize the [Bitwarden cli], for a password manager so you never have to see/know your argocd password.

## And more!

Want to get started with argocd? If you've installed it via smol-k8s-lab, then you can jump [here](https://github.com/jessebot/argo-example#argo-via-the-gui). Otherwise, if you want to start from scratch, start [here](https://github.com/jessebot/argo-example#argocd)

<!-- k8s distro link references -->
[k3s]: https://k3s.io/
[k3d]: https://k3d.io/
[KinD]: https://kind.sigs.k8s.io/
[k0s]: https://k0sproject.io/

<!-- k8s apps link references -->
[metallb]: https://github.io/metallb/metallb "metallb"
[Local Path Provisioner]: https://github.com/rancher/local-path-provisioner
[nginx-ingress]: https://github.io/kubernetes/ingress-nginx
[cert-manager]: https://cert-manager.io/docs/

<!-- k8s optional apps link references -->
[ESO]: https://external-secrets.io/v0.8.1/
[Argo CD]:https://argo-cd.readthedocs.io/en/latest/
[cilium]: https://github.com/cilium/cilium/tree/v1.14.1/install/kubernetes/cilium
[Bitwarden ESO Provider]: https://github.com/jessebot/bitwarden-eso-provider
[k8tz]: https://github.com/small-hack/argocd-apps/tree/main/alpha/k8tz
[k8up]: https://k8up.io
[Kyverno]: https://github.com/kyverno/kyverno/
[kepler]: https://github.com/sustainable-computing-io/kepler-helm-chart/tree/main/chart/kepler
[Keycloak]: https://github.com/bitnami/charts/tree/main/bitnami/keycloak/templates
[Mastodon]: https://joinmastodon.org/
[minio]: https://min.io/
[Prometheus Stack]: https://github.com/small-hack/argocd-apps/tree/main/prometheus
[Nextcloud]: https://github.com/nextcloud/helm
[Vouch]: https://github.com/jessebot/vouch-helm-chart
[Zitadel]: https://github.com/zitadel/zitadel-charts/tree/main

<!-- k8s tooling reference -->
[k9s]: https://k9scli.io/topics/install/

<!-- smol-k8s-lab dependency lib link references -->
[Poetry]: https://python-poetry.org/
[rich]: https://github.com/Textualize/richP
[PyYAML]: https://pyyaml.org/
[bcrypt]: https://pypi.org/project/bcrypt/
[click]: https://pypi.org/project/click/
[Bitwarden cli]: https://bitwarden.com/help/cli/
