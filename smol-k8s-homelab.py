#!/usr/bin/env python3
# AUTHOR: @jessebot
# Works with k3s
from argparse import ArgumentParser
import bcrypt
from collections import OrderedDict
from lib.homelabHelm import helm
from lib.util import sub_proc, simple_loading_bar, header
from lib.bw_cli import BwCLI
from os import path
from sys import exit
import yaml


PWD = path.dirname(__file__)


def parse_args():
    """
    Parse arguments and return dict
    """
    k9_help = 'Run k9s as soon as this script is complete, defaults to False'
    a_help = 'Install Argo CD as part of this script, defaults to False'
    f_help = 'Full path and name of yml to parse, e.g. -f /tmp/config.yml'
    k_help = ('distribution of kubernetes to install: \n'
              'k3s or kind. k0s coming soon')
    d_help = 'Delete the existing cluster, REQUIRES -k/--k8s [k3s|kind]'
    s_help = 'Install bitnami sealed secrets, defaults to False'
    p_help = ('Store generated admin passwords directly into your password '
              'manager. Right now, this defaults to Bitwarden and requires you'
              ' to input your vault password to unlock the vault temporarily.')
    e_help = ('Install the external secrets operator to pull secrets from '
              'somewhere else, so far only supporting gitlab')
    p = ArgumentParser(description=main.__doc__)

    p.add_argument('-k', '--k8s', required=True, help=k_help)
    p.add_argument('-f', '--file', default='./config.yml', type=str,
                   help=f_help)
    p.add_argument('--k9s', action='store_true', default=False, help=k9_help)
    p.add_argument('--argo', action='store_true', default=False, help=a_help)
    p.add_argument('-s', '--sealed_secrets', action='store_true',
                   default=False, help=s_help)
    p.add_argument('-e', '--external_secret_operator', action='store_true',
                   default=False, help=e_help)
    p.add_argument('-p', '--password_manager', action='store_true',
                   default=False, help=p_help)
    p.add_argument('--delete', action='store_true', default=False, help=d_help)

    return p.parse_args()


def add_default_repos(k8s_distro, argo=True):
    """
    Add all the default helm chart repos:
    - metallb is for loadbalancing and assigning ips, on metal...
    - ingress-nginx allows us to do ingress, so access outside the cluster
    - jetstack is for cert-manager for TLS certs
    - sealed-secrets - for encrypting k8s secrets files for checking into git
    - argo is argoCD to manage k8s resources in the future through a gui
    """
    repos = OrderedDict()

    repos['metallb'] = 'https://metallb.github.io/metallb'
    repos['ingress-nginx'] = 'https://kubernetes.github.io/ingress-nginx'
    repos['jetstack'] = 'https://charts.jetstack.io'
    repos['sealed-secrets'] = 'https://bitnami-labs.github.io/sealed-secrets'
    repos['external-secrets'] = 'https://charts.external-secrets.io'
    if argo:
        repos['argo-cd'] = 'https://argoproj.github.io/argo-helm'

    # kind has a special install path
    if k8s_distro == 'kind':
        repos.pop('ingress-nginx')

    for repo_name, repo_url in repos.items():
        helm.repo(repo_name, repo_url).add()

    # update any repos that are out of date
    helm.repo.update()


def install_k8s_distro(k8s_distro=""):
    """
    install a specific distro of k8s
    options: k3s, kind | coming soon: k0s
    """
    sub_proc(f"{PWD}/{k8s_distro}/quickstart.sh")


def install_custom_resource(custom_resource_dict):
    """
    Does a kube apply on a custom resource dict, and retries if it fails
    """
    # loops until this succeeds
    while True:
        try:
            # Write a YAML representation of data to 'k8s_cr.yaml'.
            with open('/tmp/k8s_cr.yml', 'w') as cr_file:
                yaml.dump(custom_resource_dict, cr_file)

            sub_proc('kubectl apply -f /tmp/k8s_cr.yml')
            break

        except Exception as reason:
            print(f"Hmmm, that didn't work because: {reason}")
            simple_loading_bar(3)
            continue


def configure_metallb(address_pool):
    """
    metallb is special because it has Custom Resources
    """
    # install chart and wait
    release = helm.chart(chart_name='metallb/metallb',
                         release_name='metallb',
                         namespace='kube-system')
    release.install(True)

    ip_pool_cr = {
        'apiVersion': 'metallb.io/v1beta1',
        'kind': 'IPAddressPool',
        'metadata': {'name': 'base-pool',
                     'namespace': 'kube-system'},
        'spec': {'addresses': [address_pool]}
    }
    print(ip_pool_cr)

    l2_advert_cr = {
        'apiVersion': 'metallb.io/v1beta1',
        'kind': 'L2Advertisement',
        'metadata': {'name': 'base-pool',
                     'namespace': 'kube-system'}
    }

    for custom_resource in [ip_pool_cr, l2_advert_cr]:
        install_custom_resource(custom_resource)


def configure_cert_manager(email_addr):
    """
    installs cert-manager helm chart and letsencrypt-staging clusterissuer
    """
    # install chart and wait
    release = helm.chart(release_name='cert-manager',
                         chart_name='jetstack/cert-manager',
                         namespace='kube-system',
                         set_options={'installCRDs': 'true'})
    release.install(True)

    acme_staging = 'https://acme-staging-v02.api.letsencrypt.org/directory'
    issuer = {'apiVersion': 'cert-manager.io/v1',
              'kind': 'ClusterIssuer',
              'metadata': {'name': 'letsencrypt-staging'},
              'spec': {
                  'acme': {'email': email_addr,
                           'server': acme_staging,
                           'privateKeySecretRef': {
                               'name': 'letsencrypt-staging'},
                           'solvers': [
                               {'http01': {'ingress': {'class': 'nginx'}}}]
                           }}}

    install_custom_resource(issuer)


def delete_cluster(k8s_distro="k3s"):
    """
    Delete a KIND or K3s cluster entirely.
    """
    header(f"ヾ(^_^) byebye {k8s_distro}!!")

    if k8s_distro == 'k3s':
        sub_proc('k3s-uninstall.sh')
    elif k8s_distro == 'kind':
        sub_proc('kind delete cluster')
    elif k8s_distro == 'k0s':
        header("┌（・Σ・）┘≡З  Whoops. k0s not YET supported.")


def main():
    """
    Quickly install a k8s distro for a homelab setup. Installs k3s
    with metallb, nginx-ingess-controller, cert-manager, and argo
    """
    args = parse_args()

    # make sure we got a valid k8s distro
    if args.k8s not in ['k3s', 'kind']:
        print(f'Sorry, {args.k8s} is not a currently supported k8s distro :( '
              'Please try again with either -k k3s or -k kind')
        exit()

    if args.delete:
        delete_cluster(args.k8s)
    else:
        with open(args.file, 'r') as yaml_file:
            input_variables = yaml.safe_load(yaml_file)

        # install the actual KIND or k3s cluster
        if args.k8s == 'kind':
            header('Installing KinD cluster. ' +
                   'This could take 2-3 minutes ʕ•́ᴥ•̀ʔっ♡')
        else:
            header(f"Installing {args.k8s} cluster.")
        install_k8s_distro(args.k8s)

        # this is where we add all the helm repos we're going to use
        header("Adding/Updating helm repos...")
        add_default_repos(args.k8s, args.argo)

        # needed for metal installs
        header("Configuring metallb so we have an ip address pool")
        configure_metallb(input_variables['address_pool'])

        # KinD has ingress-nginx install
        if args.k8s == 'kind':
            url = 'https://raw.githubusercontent.com/kubernetes/' + \
                  'ingress-nginx/main/deploy/static/provider/kind/deploy.yaml'
            sub_proc(f'kubectl apply -f {url}')

            # this is to wait for the deployment to come up
            sub_proc('kubectl rollout status '
                     'deployment/ingress-nginx-controller -n ingress-nginx')
            sub_proc('kubectl wait --for=condition=ready pod '
                     '--selector=app.kubernetes.io/component=controller '
                     '--timeout=90s -n ingress-nginx')
        else:
            # you need this to access webpages from outside the cluster
            header("Installing nginx-ingress-controller...")
            nginx_chart_opts = {'hostNetwork': 'true',
                                'hostPort.enabled': 'true'}
            release = helm.chart(release_name='nginx-ingress',
                                 chart_name='ingress-nginx/ingress-nginx',
                                 namespace='kube-system',
                                 set_options=nginx_chart_opts)
            release.install()

        # this is for manager SSL/TLS certificates via lets-encrypt
        header("Installing cert-manager for TLS certificates...")
        configure_cert_manager(input_variables['email'])

        # this allows you to check your secret files into git
        if args.sealed_secrets:
            header("Installing Bitnami sealed-secrets...")
            release = helm.chart(release_name='sealed-secrets',
                                 chart_name='sealed-secrets/sealed-secrets',
                                 namespace='sealed-secrets',
                                 set_options={'namespace': "sealed-secrets"})
            release.install()
            print("Installing kubeseal with brew...")
            # TODO: check if installed before running this
            sub_proc("brew install kubeseal", True)

        # this is for external secrets, like from gitlab
        if args.external_secret_operator:
            header("Installing External Secrets Operator...")
            release = helm.chart(release_name='external-secrets-operator',
                                 chart_name='external-secrets/external-secrets',
                                 namespace='external-secrets')

        # then install argo CD :D
        if args.argo:
            argocd_domain = input_variables['domains']['argocd']
            opts = {'dex.enabled': 'false',
                    'server.ingress.enabled': 'true',
                    'server.ingress.ingressClassName': 'nginx',
                    'server.ingress.hosts[0]': argocd_domain,
                    'server.extraArgs[0]': '--insecure'}

            # if we're using a password manager, generate a password & save it
            if args.password_manager:
                # if we're using bitwarden...
                bw = BwCLI()
                bw.unlock()
                argo_password = bw.generate()
                bw.create_login(name=argocd_domain,
                                item_url=argocd_domain,
                                user="admin",
                                password=argo_password)
                bw.lock()
                admin_pass = bcrypt.hashpw(argo_password.encode('utf-8'),
                                           bcrypt.gensalt()).decode()

                # this gets passed to the helm cli, but is bcrypted
                opts['configs.secret.argocdServerAdminPassword'] = admin_pass

            release = helm.chart(release_name='argo-cd',
                                 chart_name='argo/argo-cd',
                                 namespace='argocd',
                                 set_options=opts)
            release.install(True)

    print("Smol K8s Homelab Script complete :)")


if __name__ == '__main__':
    main()
