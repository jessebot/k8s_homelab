#!/usr/bin/env python3.11
"""
       Name: ingress_nginx_controller
DESCRIPTION: install the ingress nginx controller
     AUTHOR: @jessebot, @cloudymax
    LICENSE: GNU AFFERO GENERAL PUBLIC LICENSE Version 3
"""
# external libraries
import logging as log

# internal libraries
from smol_k8s_lab.k8s_tools.argocd_util import install_with_argocd, check_if_argocd_app_exists
from os import path
from smol_k8s_lab.k8s_tools.helm import Helm
from smol_k8s_lab.k8s_tools.k8s_lib import K8s
from smol_k8s_lab.utils.subproc import subproc


def configure_ingress_nginx(k8s_obj: K8s, k8s_distro: str, prometheus: bool = False) -> None:
    """
    install nginx ingress controller from manifests for kind and helm for k3s
    """
    if k8s_distro == 'kind':
        # TODO: Pin this version? 🤷
        url = ('https://raw.githubusercontent.com/kubernetes/ingress-nginx'
               '/main/deploy/static/provider/kind/deploy.yaml')

        # this is to wait for the deployment to come up
        if prometheus:
            nginx_chart_opts = {"prometheus.create": prometheus,
                                "prometheus.port": "9901"}
            k8s_obj.apply_manifests(
                    url,
                    "ingress-nginx",
                    "ingress-nginx-controller",
                    "app.kubernetes.io/component=controller",
                    set_options=nginx_chart_opts
                    )

            # deploy the metrics service
            full_path = path.realpath(__file__)
            file_path, filename = path.split(full_path)
            kubeapply = f'kubectl apply -f {file_path}/nginx-metrics-service.yaml'
            subproc([kubeapply], spinner=True)
            return
        else:
            k8s_obj.apply_manifests(
                    url,
                    "ingress-nginx",
                    "ingress-nginx-controller",
                    "app.kubernetes.io/component=controller"
                    )
    else:
        values = {"controller.allowSnippetAnnotations": True}
        release = Helm.chart(release_name='ingress-nginx',
                             chart_name='ingress-nginx/ingress-nginx',
                             namespace='ingress-nginx',
                             set_options=values)
        release.install()


def install_ingress_nginx_argocd_app(k8s_obj: K8s, ingress_nginx_dict: dict) -> None:
    """
    install the ingress nginx Argo CD Application for easier management
    """
    if not check_if_argocd_app_exists("ingress-nginx"):
        log.info("Installing Argo CD Application: ingress-nginx")
        install_with_argocd(k8s_obj,
                            "ingress-nginx",
                            ingress_nginx_dict['argo'])
