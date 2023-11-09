from smol_k8s_lab.bitwarden.bw_cli import BwCLI, create_custom_field
from smol_k8s_lab.k8s_apps.identity_provider.zitadel_api import Zitadel
from smol_k8s_lab.k8s_tools.argocd_util import (install_with_argocd,
                                                check_if_argocd_app_exists,
                                                update_argocd_appset_secret)
from smol_k8s_lab.k8s_tools.k8s_lib import K8s
from smol_k8s_lab.utils.rich_cli.console_logging import sub_header, header
from smol_k8s_lab.utils.passwords import create_password

import logging as log


def configure_matrix(k8s_obj: K8s,
                     config_dict: dict,
                     zitadel: Zitadel,
                     bitwarden: BwCLI = None) -> bool:
    """
    creates a matrix app and initializes it with secrets if you'd like :)
    """
    header("Setting up [green]Matrix[/green], so you can self host your own chat"
           '🔢')

    app_installed = check_if_argocd_app_exists('matrix')
    secrets = config_dict['argo']['secret_keys']
    if secrets:
        matrix_hostname = secrets['hostname']

    # initial secrets to deploy this app from scratch
    if config_dict['init']['enabled'] and not app_installed:
        init_values = config_dict['init']['values']

        # configure s3 credentials if they're in use
        s3_access_id = init_values.get('s3_access_id', 'matrix')
        s3_access_key = init_values.get('s3_access_key', '')
        s3_endpoint = secrets.get('s3_endpoint', "")
        s3_bucket = secrets.get('s3_bucket', "matrix")
        if config_dict['argo']['directory_recursion']:
            default_minio = True
        else:
            default_minio = False
        create_minio_tenant = init_values.get('create_minio_tenant',
                                              default_minio)

        # configure the smtp credentials
        smtp_user = init_values['smtp_user']
        smtp_pass = init_values['smtp_password']
        smtp_host = init_values['smtp_host']

        # creates the initial root credentials secret for the minio tenant
        if create_minio_tenant:
            if not s3_access_key:
                s3_access_key = create_password()
            credentials_exports = {
                    'config.env': f"""MINIO_ROOT_USER={s3_access_id}
            MINIO_ROOT_PASSWORD={s3_access_key}"""}
            k8s_obj.create_secret('default-tenant-env-config', config_dict['argo']['namespace'],
                                  credentials_exports)

        # create Matrix OIDC Application
        if zitadel:
            log.debug("Creating a Matrix OIDC application in Zitadel...")
            idp_id = "zitadel"
            idp_name = "Zitadel Auth"
            redirect_uris = f"https://{matrix_hostname}/_synapse/client/oidc/callback"
            logout_uris = [f"https://{matrix_hostname}"]
            matrix_dict = zitadel.create_application("matrix",
                                                     redirect_uris,
                                                     logout_uris)
            zitadel.create_role("matrix_users", "Matrix Users", "matrix_users")
            zitadel.update_user_grant(['matrix_users'])

        # if the user has bitwarden enabled
        if bitwarden:
            sub_header("Creating matrix secrets in Bitwarden")

            # S3 credentials
            s3_host_obj = create_custom_field("s3Endpoint", s3_endpoint)
            s3_bucket_obj = create_custom_field("s3Bucket", s3_bucket)
            s3_id = bitwarden.create_login(
                    name='matrix-s3-credentials',
                    item_url=matrix_hostname,
                    user=s3_access_id,
                    password=s3_access_key,
                    fields=[s3_host_obj, s3_bucket_obj]
                    )

            # postgresql credentials
            matrix_pgsql_password = bitwarden.generate()
            db_hostname_obj = create_custom_field(
                    "hostname",
                    f"matrix-postgres-rw.{config_dict['argo']['namespace']}.svc"
                    )
            db_pass_obj = create_custom_field("postgresPassword",
                                              matrix_pgsql_password)
            # the database name
            db_obj = create_custom_field("database", "matrix")
            db_id = bitwarden.create_login(
                    name='matrix-pgsql-credentials',
                    item_url=matrix_hostname,
                    user='matrix',
                    password=matrix_pgsql_password,
                    fields=[db_hostname_obj, db_pass_obj, db_obj]
                    )

            # SMTP credentials
            matrix_smtp_host_obj = create_custom_field("smtpHostname", smtp_host)
            smtp_id = bitwarden.create_login(
                    name='matrix-smtp-credentials',
                    item_url=matrix_hostname,
                    user=smtp_user,
                    password=smtp_pass,
                    fields=[matrix_smtp_host_obj]
                    )

            # registration key
            matrix_registration_key = bitwarden.generate()
            reg_id = bitwarden.create_login(
                    name='matrix-registration-key',
                    item_url=matrix_hostname,
                    user="admin",
                    password=matrix_registration_key
                    )

            # OIDC credentials
            log.info("Creating OIDC credentials for Matrix in Bitwarden")
            if zitadel:
                issuer_obj = create_custom_field("issuer", "https://" + zitadel.hostname)
                idp_id_obj = create_custom_field("idp_id", idp_id)
                idp_name_obj = create_custom_field("idp_name", idp_name)
                oidc_id = bitwarden.create_login(
                        name='matrix-oidc-credentials',
                        item_url=matrix_hostname,
                        user=matrix_dict['client_id'],
                        password=matrix_dict['client_secret'],
                        fields=[issuer_obj, idp_id_obj, idp_name_obj]
                        )

            # update the matrix values for the argocd appset
            update_argocd_appset_secret(
                    k8s_obj,
                    {'matrix_registration_credentials_bitwarden_id': reg_id,
                     'matrix_smtp_credentials_bitwarden_id': smtp_id,
                     'matrix_s3_credentials_bitwarden_id': s3_id,
                     'matrix_postgres_credentials_bitwarden_id': db_id,
                     'matrix_oidc_credentials_bitwarden_id': oidc_id,
                     'matrix_idp_name': idp_name,
                     'matrix_idp_id': idp_id})

            # reload the bitwarden ESO provider
            try:
                k8s_obj.reload_deployment('bitwarden-eso-provider', 'external-secrets')
            except Exception as e:
                log.error(
                        "Couldn't scale down the [magenta]bitwarden-eso-provider[/]"
                        "deployment in [green]external-secrets[/] namespace. Recieved: "
                        f"{e}"
                        )

        # else create these as Kubernetes secrets
        else:
            # postgresql credentials
            matrix_pgsql_password = create_password()
            k8s_obj.create_secret('matrix-pgsql-credentials', 'matrix',
                                  {"password": matrix_pgsql_password})

            # registation key
            matrix_registration_key = create_password()
            k8s_obj.create_secret('matrix-registration', 'matrix',
                                  {"registrationSharedSecret": matrix_registration_key})

            # oidc secret
            k8s_obj.create_secret(
                    'matrix-oidc-credentials',
                    'matrix',
                    {'user': matrix_dict['client_id'],
                     'password': matrix_dict['client_secret'],
                     'issuer': zitadel.hostname}
                    )

    if not app_installed:
        install_with_argocd(k8s_obj, 'matrix', config_dict['argo'])
    else:
        log.info("matrix already installed 🎉")
        # update the matrix values for the argocd appset
        if bitwarden and config_dict['init']['enabled']:
            log.debug("making sure matrix bitwarden IDs are present in appset "
                      "secret plugin")
            reg_id = bitwarden.get_item(
                    f"matrix-registration-key-{matrix_hostname}"
                    )[0]['id']
            smtp_id = bitwarden.get_item(
                    f"matrix-smtp-credentials-{matrix_hostname}"
                    )[0]['id']
            s3_id = bitwarden.get_item(
                    f"matrix-s3-credentials-{matrix_hostname}"
                    )[0]['id']
            db_id = bitwarden.get_item(
                    f"matrix-pgsql-credentials-{matrix_hostname}"
                    )[0]['id']
            oidc_id = bitwarden.get_item(
                    f"matrix-oidc-credentials-{matrix_hostname}"
                    )[0]

            # identity provider name and id are nested in the oidc item fields
            for field in oidc_id['fields']:
                if field['name'] == 'idp_id':
                    idp_id = field['value']
                if field['name'] == 'idp_name':
                    idp_name = field['value']

            update_argocd_appset_secret(
                    k8s_obj,
                    {'matrix_registration_credentials_bitwarden_id': reg_id,
                     'matrix_smtp_credentials_bitwarden_id': smtp_id,
                     'matrix_s3_credentials_bitwarden_id': s3_id,
                     'matrix_postgres_credentials_bitwarden_id': db_id,
                     'matrix_oidc_credentials_bitwarden_id': oidc_id['id'],
                     'matrix_idp_name': idp_name,
                     'matrix_idp_id': idp_id})
