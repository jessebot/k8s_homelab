#!/usr/bin/env python3.11
"""
       Name: nginx_ingress_controller
DESCRIPTION: install the nginx ingress controller
     AUTHOR: @jessebot
    LICENSE: GNU AFFERO GENERAL PUBLIC LICENSE Version 3
"""
from smol_k8s_lab.k8s_tools.helm import Helm
from smol_k8s_lab.k8s_tools.k8s_lib import K8s


def configure_ingress_nginx(k8s_obj: K8s, k8s_distro: str) -> None:
    """
    install nginx ingress controller from manifests for kind and helm for k3s
    """
    url = ('https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/'
           'deploy/static/provider/kind/deploy.yaml')

    if k8s_distro == 'kind':
        # this is to wait for the deployment to come up
        k8s_obj.apply_manifests(
                url,
                "ingress-nginx",
                "ingress-nginx-controller",
                "app.kubernetes.io/component=controller"
                )
    else:
        release = Helm.chart(release_name='ingress-nginx',
                             chart_name='ingress-nginx/ingress-nginx',
                             namespace='ingress-nginx')
        release.install()
