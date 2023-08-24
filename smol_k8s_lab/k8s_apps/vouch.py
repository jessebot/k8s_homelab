from rich.prompt import Prompt
from ..k8s_tools.argocd_util import install_with_argocd
from ..k8s_tools.k8s_lib import K8s
from ..pretty_printing.console_logging import header
from ..utils.bw_cli import BwCLI, create_custom_field


def configure_vouch(k8s_obj: K8s,
                    vouch_config_dict: dict = {},
                    vouch_client_credentials: dict = {},
                    base_url: str = "",
                    bitwarden: BwCLI = None) -> bool:
    """
    Installs vouch-proxy as an Argo CD application on Kubernetes

    Takes Args:
          k8s_obj:                  K8s(), for the authenticated k8s client
          vouch_config_dict:        dict, Argo CD parameters
          vouch_client_credentials: dict, OIDC client credentials
          base_url:                 str, OIDC URL for keycloak or zitadel
          bitwarden:                BwCLI, to store k8s secrets in bitwarden

    returns True if successful
    """
    header("🗝️ Vouch Setup")

    if vouch_config_dict['init']:
        secrets = vouch_config_dict['secret_keys']
        vouch_hostname = secrets['vouch_hostname']
        client_secret = vouch_client_credentials['client_secret']
        client_id = vouch_client_credentials['client_id']

        vouch_callback_url = f'https://{vouch_hostname}/auth'
        m = ("[green]Please enter a comma seperated list of emails that are "
             "allowed to access domains behind Vouch")
        emails = Prompt.ask(m)
        m = ("[green]Please enter a comma seperated list of domains that are "
             "allowed to use Vouch")
        domains = Prompt.ask(m)

        # if using bitwarden, put the secret in bitarden and ESO will grab it
        if bitwarden:
            auth_url = create_custom_field("authUrl", f'{base_url}auth')
            token_url = create_custom_field("tokenUrl", f'{base_url}token')
            user_info_url = create_custom_field("userInfoUrl", f'{base_url}userinfo')
            callback_urls = create_custom_field("callbackUrls", vouch_callback_url)
            # create oauth OIDC bitwarden item
            bitwarden.create_login(name='vouch-oauth-config',
                                   user=client_id,
                                   password=client_secret,
                                   fields=[auth_url,
                                           token_url,
                                           user_info_url,
                                           callback_urls])

            domains_obj = create_custom_field("domains", domains)
            emails_obj = create_custom_field("allowList", emails)
            # create vouch config bitwarden item
            bitwarden.create_login(name='vouch-config',
                                   user='vouch',
                                   password='',
                                   fields=[domains_obj, emails_obj])
        # create vouch k8s secrets if we're not using bitwarden
        else:
            # create oauth OIDC k8s secret
            k8s_obj.create_secret('vouch-oauth-config', 'vouch',
                                  {'user': client_id,
                                   'password': client_secret,
                                   'authUrl': f'{base_url}/auth',
                                   'tokenUrl': f'{base_url}/token',
                                   'userInfoUrl': f'{base_url}/userinfo',
                                   'callbackUrls': vouch_callback_url})

            # create vouch config k8s secret
            k8s_obj.create_secret('vouch-config', 'vouch',
                                  {'domains': domains, 'allowList': emails})

    install_with_argocd(k8s_obj, 'vouch', vouch_config_dict['argo'])
    return True 
