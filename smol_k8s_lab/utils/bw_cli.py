#!/usr/bin/env python3
# extremely simple bitwarden cli wrapper
# Author: @jessebot jessebot@linux.com
"""
Example:
        bw = BwCLI()
        bw.unlock()
        bw.generate()
        bw.create_login(name="test mctest",
                        item_url="coolhosting4dogs.tech",
                        user="admin",
                        password="fakepassword")
        bw.lock()
"""
import base64
import json
import logging as log
from rich.prompt import Prompt
from shutil import which
from sys import exit
from os import environ
from ..subproc import subproc


class BwCLI():
    """
    Python Wrapper for the Bitwarden cli
    """
    def __init__(self, overwrite: bool = False):
        """
        This is mostly for storing the session, credentials, and overwrite bool
        """
        self.bw_path = which("bw")
        if not self.bw_path:
            log.error("whoops, looks like bw isn't installed. "
                      "Try brew install bw")
            exit()
        # if we clean up the session when we're done or not
        self.delete_session = True

        # make sure there's not a session token in the env vars already
        self.session = environ.get("BW_SESSION", None)

        self.host = environ.get("BW_HOST", default="https://bitwarden.com")
        log.debug(f"Using {self.host} as $BW_HOST")

        # get password from env var, and if empty, prompt user for input
        self.password = environ.get("BW_PASSWORD",
                                    self.__get_credential__("password"))

        # get clientID from env var, and if empty, prompt user for input
        self.client_id = environ.get("BW_CLIENTID",
                                    self.__get_credential__("clientID"))

        # get clientSecret from env var, and if empty, prompt user for input
        self.client_secret = environ.get("BW_CLIENTSECRET",
                                    self.__get_credential__("clientSecret"))

        # controls if we overwrite the existing items when creating new items
        self.overwrite = overwrite

    def __get_credential__(self, credential: str = ""):
        """
        prompts a user for a specific credential
        """
        cred_prompt = f"[cyan]🤫 Enter your Bitwarden vault {credential}"
        credential = Prompt.ask(cred_prompt, password=True)
        return credential

    def status(self):
        """
        generate a new password. Takes special_characters bool.
        """
        log.info('Checking if you are logged in...')
        vault_status = json.loads(subproc(["bw status"], quiet=True))['status']

        return vault_status

    def unlock(self):
        """
        unlocks the local bitwarden vault, and returns session token
        """

        if self.session:
            log.info('Using session token from $BW_SESSION env variable')
            self.delete_session = False
        else:
            status = self.status()

            # verify we're even logged in :)
            if status == "unauthenticated":
                log.info('Logging into the Bitwarden vault...')
                # set command to login if we're unauthenticated
                cmd = (f"{self.bw_path} login --passwordenv BW_PASSWORD "
                       "--apikey --raw")
            else:
                log.info('Unlocking the Bitwarden vault...')
                # default command is unlock
                cmd = f"{self.bw_path} unlock --passwordenv BW_PASSWORD --raw"

            # run either bw login or bw unlock depending on bw status
            self.session = subproc([cmd],
                                   env={"BW_PASSWORD": self.password,
                                        "BW_CLIENTID": self.client_id,
                                        "BW_CLIENTSECRET": self.client_secret,
                                        "BW_HOST": self.host})
            log.info('Unlocked the Bitwarden vault.')

    def lock(self) -> None:
        """
        lock bitwarden vault, only if the user didn't have a session env var
        """
        if self.delete_session:
            log.info('Locking the Bitwarden vault...')
            subproc([f"{self.bw_path} lock"], env={"BW_SESSION": self.session})
            log.info('Bitwarden vault locked.')

    def generate(self, special_characters=False):
        """
        generate a new password. Takes special_characters bool.
        """
        log.info('Generating a new password...')

        command = "bw generate --length 32 --uppercase --lowercase --number"
        if special_characters:
            command += " --special"

        password = subproc([command], quiet=True)
        log.info('New password generated.')
        return password

    def get_item(self, item_name: str = ""):
        """
        Get Item and return False if it does not exist else return the item ID
        Required Args:
            - item_name: str of name of item
        """
        command = f"{self.bw_path} get item {item_name}"
        response = subproc([command], error_ok=True,
                           env={"BW_SESSION": self.session})
        if 'Not found.' in response:
            return False
        else:
            return json.loads(response)['id']

    def delete_item(self, item_id: str = ""):
        """
        Delete Item
            - item_name: str of name of item
        """
        command = f"{self.bw_path} delete item {item_id}"
        subproc([command], error_ok=True,
                env={"BW_SESSION": self.session})
        return

    def create_login(self, name="", item_url=None, user="", password="",
                     fields={}, org=None, collection=None):
        """
        Create login item to store a set of credentials for one site.
        Required Args:
            - name:        str of the name of the item to create in the vault
        Optional Args:
            - user:        str of username to use for login item
            - password:    str of password you want to use for login item
            - item_url:    str of URL you want to use the credentials for
            - org:         str of organization to use for collection
            - collection:  str
        """
        item = self.get_item(name)

        if item:
            if self.overwrite:
                log.info("bitwarden.overwrite set to true, so we will delete"
                         f"the existing item: {item}")
                self.delete_item(item)
            else:
                err = (f"😵 Item named {name} already exists in your Bitwarden"
                       " vault and bitwarden.overwrite is set to false. We "
                       "will create the item anyway, but the Bitwarden ESO "
                       "Provider may have trouble finding it :(")
                log.error(err)

        log.info('Creating bitwarden login item...')
        login_obj = json.dumps({
            "organizationId": org,
            "collectionIds": collection,
            "folderId": None,
            "type": 1,
            "name": item_url,
            "notes": None,
            "favorite": False,
            "fields": [fields],
            "login": {"uris": [{"match": 0,
                                "uri": item_url}],
                      "username": user,
                      "password": password,
                      "totp": None},
            "secureNote": None,
            "card": None,
            "identity": None,
            "reprompt": 0})

        encodedBytes = base64.b64encode(login_obj.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")

        subproc([f"{self.bw_path} create item {encodedStr}"],
                env={"BW_SESSION": self.session})
        log.info('Created bitwarden login item.')
