#!/usr/bin/env python3
# Author: @jessebot jessebot@linux.com
from getpass import getpass
import subprocess
from requests import post, get
from util import header


class BwRest():
    """
    Python Wrapper for the Bitwarden REST API
    api ref: https://bitwarden.com/help/vault-management-api/
    """
    def __init__(self, domain="localhost", port=8087, https=False,
                 serve_local_api=True):
        """
        If serve_local_api=True, serve the bw api temporarily if it's not
        already there. Defaults to running on http://localhost:8087

        Accepts domain str, port int, https bool, and serve_local_api bool

        example cli run: bw serve --hostname bwapi.mydomain.com --port 80
        """
        # Cleanup=False means we don't have to kill any processes after this
        self.cleanup = False

        if serve_local_api:
            # Cleanup means we'll be killing this process when we're done
            self.cleanup = True
            api_cmd = "bw serve"
            if domain != 'localhost':
                api_cmd += " --hostname {domain} "
            if port != 8087:
                api_cmd += " --port {port}"
            self.bw_process = subprocess.Popen(api_cmd.split())

        self.url = f"http://{domain}:{port}"
        if https:
            self.url = f"https://{domain}:{port}"

        self.loginItem.url = self.url
        self.data_obj = {'session': ""}
        self.loginItem.data_obj = self.data_obj

    def __terminate(self):
        """
        kills the running bitwarden rest api process. if this doesn't run,
        the bitwarden rest api will remain.
        """
        # only kill the process if we created it ourselves
        if self.bw_process:
            print("Killing the bitwarden rest api, since we're done with it.")
            self.bw_process.kill()
        return

    def generate(self, special_characters=False):
        """
        generate a new password. Takes special_characters bool.
        if we get an error, return that whole json blob response
        """
        header('Generating a new password...')

        # This is for the complexity of the password
        data_obj = {'length': 18, 'uppercase': True, 'lowercase': True,
                    'number': True}
        if special_characters:
            data_obj['special'] = True

        res = get(f"{self.url}/generate", json=data_obj).json()

        if res['success']:
            print(res['data']['data'])
            return res['data']['data']
        else:
            return res

    def unlock(self):
        """
        unlocks the local bitwarden vault, and returns session token
        if we get an error, return that whole json blob response
        TODO: check local env vars for password or api key
        """
        print("We'll need you to enter your password for bitwarden to unlock"
              "your vault temporarily to add the new password")
        password_prompt = 'Enter your Bitwarden Password: '
        password = getpass(prompt=password_prompt, stream=None)

        header('Unlocking the Bitwarden vault...')
        data_obj = {'password': password}
        res = post(f'{self.url}/unlock', json=data_obj).json()

        if res['success']:
            header(res['data']['title'], False)
            self.data_obj['session'] = res['data']['raw']
        else:
            return res

    def lock(self):
        """
        lock the local bitwarden vault
        """
        header('Locking the Bitwarden vault...')

        res = post(f"{self.url}/lock", json=self.data_obj).json()

        if res['success']:
            header(res['data']['title'], False)
            msg = res['data']['message']
            if msg:
                print(msg)
            self.__terminate()
        else:
            return res

    class loginItem():
        def __init__(self, **kwargs):
            """
            kwarg: name="", item_url="", user="", password="", org="",
                   collection=""
            Get, modify, and create login items, and only login items
            takes optional organization and collection
            """
            self.collection = None
            self.org = None
            self.req_url = f"{self.url}/object/item/"
            self.__dict__.update(kwargs)

        def create(self):
            """
            creates a new bitwarden login item via POST to {URL}/object/item
            Returns: {'success': True,
                      'data': {'object': 'item',
                               'id': '84b9d020-bce6-443b-8d6c-aef300890b83',
                               'totp': None, 'passwordRevisionDate': None},
                               'revisionDate': '2022-08-16T08:18:57.786Z',
                               'deletedDate': None}}
            """
            header('Creating bitwarden login item...')
            login_data_obj = {"organizationId": self.org,
                              "collectionId": self.collection,
                              "folderId": None,
                              "type": 1,
                              "name": self.item_url,
                              "notes": None,
                              "favorite": False,
                              "fields": [],
                              "login": {"uris": [{"match": 0,
                                                  "uri": self.item_url}],
                                        "username": self.user,
                                        "password": self.password,
                                        "totp": None},
                              "reprompt": 0}
            login_data_obj.update(self.data_obj)

            res = post(self.req_url, json=login_data_obj).json()
            if res['success']:
                header(f"Successfully created {self.item_url} with id: "
                       f"{res['data']['id']}")
                return res['data']['id']
            else:
                print(res)
                return res


def existing_bw_rest_api():
    """
    check for existing bw rest apis running
    """
    # TODO : use psutil to ensure we don't have another rest api running
    return


def main():
    """
    main function to run through a test of every function
    """
    bw_instance = BwRest()
    bw_instance.unlock()
    bw_instance.generate()
    # kwarg: name="", item_url="", user="", password="", org="", collection=""
    login_item = bw_instance.loginItem(name="test mctest",
                                       item_url="test.tech",
                                       user="admin",
                                       password="fakepassword")
    login_item.create()
    bw_instance.lock()


if __name__ == '__main__':
    main()
