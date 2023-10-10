from smol_k8s_lab.tui.base import BaseApp
from smol_k8s_lab.utils.rich_cli.console_logging import print_msg
import sys


def launch_config_tui():
    """
    Run all the TUI screens
    """
    res = BaseApp().run()
    if not res:
        print_msg("[blue]♥[/] [cyan]Have a nice day[/] [blue]♥\n", style="italic")
        sys.exit()

    cluster_name = res[0]
    config = res[1]
    bitwarden_credentials = res[2]

    # assume there's no secrets
    secrets = {}

    # check if we're using the appset_secret_plugin at all
    if config['apps']['appset_secret_plugin']['enabled']:
        # if we are using the appset_secret_plugin, then grab all the secret keys
        for app, metadata in config['apps'].items():
            if metadata['enabled']:
                secret_keys = metadata['argo'].get('secret_keys', None)
                if secret_keys:
                    for key, value in secret_keys.items():
                        secrets[f"{app}_{key}"] = value

        # this is to set the cluster issuer for all applications
        global_cluster_issuer = config['apps_global_config']['cluster_issuer']
        secrets['global_cluster_issuer'] = global_cluster_issuer

    return cluster_name, config, secrets, bitwarden_credentials


def placeholder_grammar(key: str) -> str:
    """
    generates a grammatically correct placeolder string for inputs
    """
    article = ""

    # check if this is a plural (ending in s) and if ip address pool
    plural = key.endswith('s') or key == "address_pool"
    if plural:
        plural = True

    # check if the key starts with a vowel
    starts_with_vowel = key.startswith(('o','a','e'))

    # create a gramatically corrrect placeholder
    if starts_with_vowel and not plural:
        article = "an"
    elif not starts_with_vowel and not plural:
        article = "a"

    # if this is plural change the grammar accordingly
    if plural:
        return f"Please enter a comma seperated list of {key}"
    else:
        return f"Please enter {article} {key}"
