<h2 align="center">
  <img
    src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png"
    height="30"
    width="0px"
  />
smol k8s lab 🧸 <sup><sub>Now with more :squid:</sub></sup>
</h2>

<p align="center">
  <a href="https://github.com/jessebot/smol-k8s-lab/releases">
    <img src="https://img.shields.io/github/v/release/jessebot/smol-k8s-lab?style=plastic&labelColor=484848&color=3CA324&logo=GitHub&logoColor=white">
  </a>
</p>

A tool to run slimmer k8s distros on metal, with batteries included. Deploys Argo CD by default, so you can mange your entire local testing lab from the very beginning using files in [open source git repos](), and with the help of a very handy dashboard.

Also helpful for benchmarking various [k8s distros](#supported-k8s-distributions)! 💙


<p align="center">
  <a href="https://raw.githubusercontent.com/jessebot/smol-k8s-lab/main/docs/assets/images/screenshots/help_text.svg">
      <img src="./docs/assets/images/screenshots/help_text.svg" alt="Output of smol-k8s-lab --help after cloning the directory and installing the prerequisites.">
  </a>
</p>


# Installation
`smol-k8s-lab` requires Python 3.11. If you've already got it and [`brew`] installed, you should be able to:

```bash
# install the CLI
pip3.11 install smol-k8s-lab

# Check the help menu before proceeding
smol-k8s-lab --help
```

## Usage

### Initialization
After you've followed the installation instructions, if you're *new* to `smol-k8s-lab`,  initialize a new config file. To do that, just run:

```bash
# we'll walk you through any configuration needed before 
# saving the config and deploying it for you
smol-k8s-lab
```

<details>
  <summary><h3>Upgrading to v1.x</h3></summary>

If you've installed smol-k8s-lab prior to `v1.0.0`, please backup your old configuration, and then remove the `~/.config/smol-k8s-lab/config.yaml` (or `$XDG_CONFIG_HOME/smol-k8s-lab/config.yaml`) file entirely, then run the following:

```yaml
# this upgrades smol-k8s-lab
pip3.11 install --upgrade smol-k8s-lab

# this initializes a new configuration
smol-k8s-lab
```

</details>

`v2.0.0b1` is available for testing but docs and screenshots are still under development. ETA is about 1-2 weeks for those tests to be complete and the official `2.0.0` to be launched, which will support a full TUI and a range of new options in the config file. To begin testing that release (or [other pre-releases](https://pypi.org/project/smol_k8s_lab/2.0.0b1/#history)) you can do:
```bash
pip install smol_k8s_lab==2.0.0b1
```

#### Creating a new config without running smol-k8s-lab
This is helpful if you just want to take a look at the default configuration before installing any Kubernetes distros. This will also allow you to disable any default applications you'd like ahead of time.

```bash
# create the needed directory if you haven't already, NOTE: this can also be in $XDG_CONFIG_HOME/smol-k8s-lab/config.yaml
mkdir -p ~/.config/smol-k8s-lab

# download the default config file
curl -o config.yaml https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/smol_k8s_lab/config/default_config.yaml

# move the config file to the config directory (can also be $XDG_CONFIG_HOME/smol-k8s-lab/config.yaml)
mv config.yaml ~/.config/smol-k8s-lab/config.yaml
```

You can now use your text editor of choice to view and edit the default config before running `smol-k8s-lab` :)

## Configuration
You can checkout the default config file [here](./smol_k8s_lab/config/default_config.yaml). We've also got a [Quickstart guide](https://small-hack.github.io/smol-k8s-lab/quickstart) for you to jump right in :)

### Adding custom Applications

You can create any application you already have an Argo CD application repo for, by following a simple application YAML schema in `~/.config/smol-k8s-lab/config.yaml` like this:

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

### Supported k8s distributions
We always install the latest version of Kubernetes that is available from the distro's startup script.

|  Distro    |         Description              |
|:----------:|:------------------------------------------------------|
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/images/icons/k3s_icon.ico" width="26">][k3s] <br /> [k3s] | The certified Kubernetes distribution built for IoT & Edge computing |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/images/icons/k3d.png" width="26">][k3d] <br /> [k3d] | **ALPHA - TESTING PHASE** k3s in docker 🐳 |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/images/icons/kind_icon.png" width="32">][KinD] <br /> [KinD] | kind is a tool for running local Kubernetes clusters using Docker container “nodes”. kind was primarily designed for testing Kubernetes itself, but may be used for local development or CI. |

We tend to test first on k3s first, then the other distros. k3d support coming soon.

### Default Installed Applications
All of these can be disabled with the exception of Argo CD, which is optional, but if not installed, `smol-k8s-lab` will <i>only</i> install: MetalLB, nginx-ingress, and cert-manager.

|           Application           |                      Description                      | Initialization Supported |
|:-------------------------------:|:------------------------------------------------------|:------------------------:|
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/metallb_icon.png" width="32px" alt="metallb logo, blue arrow pointing up, with small line on one leg of arrow to show balance">][metallb] <br /> [metallb] | Loadbalancer and IP Address pool manager for metal | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/nginx.ico" width="32px" alt="nginx logo, white letter N with green background">][ingress-nginx] <br /> [ingress-nginx] | The ingress controller allows access to the cluster remotely, needed for web traffic | No |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/cert-manager_icon.png" width="32px" alt="cert manager logo">][cert-manager] <br /> [cert-manager] | For SSL/TLS certificates | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD] <br /> [Argo CD] | Gitops - Continuous Deployment | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/argo_icon.png" width="32" alt="argo CD logo, an organer squid wearing a fishbowl helmet">][Argo CD Appset Secret Plugin] <br /> [Argo CD Appset Secret Plugin] | Gitops - Continuous Deployment | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/eso_icon.png" width="32" alt="ESO logo, outline of robot with astricks in a screen in it's belly">][ESO] <br /> [ESO] | external-secrets-operator integrates external secret management systems like Bitwarden or GitLab | No |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/eso_icon.png" width="32" alt="ESO logo, again">][Bitwarden ESO Provider] <br /> [Bitwarden ESO Provider] | Bitwarden external-secrets-operator provider  | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/zitadel.png" width="32" alt="Zitadel logo, an orange arrow pointing left">][ZITADEL] <br /> [ZITADEL] | An identity provider and OIDC provider to provide SSO | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/vouch.png" width="32" alt="Vouch logo, the letter V in rainbow ">][Vouch] <br /> [Vouch] | Vouch proxy allows you to secure web pages that lack authentication e.g. prometheus | Yes |
| [<img src="https://raw.githubusercontent.com/small-hack/smol-k8s-lab/main/docs/assets/images/icons/prometheus.png" width="32" alt="Prometheus logo, a torch">][Prometheus Stack] <br /> [Prometheus Stack] | Prometheus monitoring and logging stack using [loki]/[promtail], [alert manager], and [grafana]  | Yes |

For a complete list of installable applications, checkout the [default apps docs](https://small-hack.github.io/smol-k8s-lab/k8s_apps/argocd/) and to install your own you can check out an [example via the config file](https://small-hack.github.io/smol-k8s-lab/config_file/#applications) or [learn how to do it via the tui](https://small-hack.github.io/smol-k8s-lab/tui/apps_screen/#adding-new-applications).


# Status
This is still in early beta, as we figure out all the apps and distros we want to support, and pin all the versions, but if you'd like to [contribute](./CONTRIBUTING.md) or just found a :bug:, feel free to open an issue (and/or pull request), and we'll try to take a look ASAP!

<!-- k8s distro link references -->
[k3s]: https://k3s.io/
[k3d]: https://k3d.io/
[KinD]: https://kind.sigs.k8s.io/

<!-- k8s optional apps link references -->
[ESO]: https://external-secrets.io/v0.8.1/
[alert manager]: https://prometheus.io/docs/alerting/latest/alertmanager/
[Argo CD]:https://argo-cd.readthedocs.io/en/latest/
[Argo CD Appset Secret Plugin]: https://github.com/jessebot/argocd-appset-secret-plugin/
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
[Vouch]: https://github.com/jessebot/vouch-helm-chart
[ZITADEL]: https://github.com/zitadel/zitadel-charts/tree/main

<!-- k8s tooling reference -->
[`brew`]: https://brew.sh
[k9s]: https://k9scli.io/topics/install/
[restic]: https://restic.readthedocs.io/en/stable/
