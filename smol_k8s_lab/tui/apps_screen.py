#!/usr/bin/env python3.11
# smol-k8s-lab libraries
from smol_k8s_lab.utils.subproc import subproc
# from smol_k8s_lab.k8s_apps.operators.postgres_operators import configure_postgres_operator
from smol_k8s_lab.k8s_tools.argocd_util import sync_argocd_app, check_if_argocd_app_exists
from smol_k8s_lab.tui.app_widgets.invalid_apps import InvalidAppsModalScreen
from smol_k8s_lab.tui.app_widgets.app_inputs_confg import AppInputs
from smol_k8s_lab.tui.app_widgets.new_app_modal import NewAppModalScreen
from smol_k8s_lab.tui.app_widgets.modify_globals import ModifyAppGlobals
from smol_k8s_lab.tui.util import format_description

# external libraries
from os import environ
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Container, Grid
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, SelectionList
from textual.widgets._toggle_button import ToggleButton
from textual.widgets.selection_list import Selection


class AppsConfigScreen(Screen):
    """
    Textual screen to display smol-k8s-lab applications for configuring
    """
    CSS_PATH = ["./css/apps_config.tcss",
                "./css/apps_init_config.tcss"]

    BINDINGS = [
            Binding(key="b,escape,q",
                    key_display="b",
                    action="app.pop_screen",
                    description="Back"),
            Binding(key="a",
                    key_display="a",
                    action="screen.launch_new_app_modal",
                    description="New App"),
            Binding(key="n",
                    key_display="n",
                    action="screen.try_next_screen",
                    description="Next")
            ]

    ToggleButton.BUTTON_INNER = '♥'

    def __init__(self, config: dict,
                 highlighted_app: str = "",
                 modify_cluster: bool = False) -> None:
        # show the footer at bottom of screen or not
        self.show_footer = self.app.cfg['smol_k8s_lab']['tui']['show_footer']

        # should be the apps section of smol k8s lab config
        self.cfg = config

        # if this is an active cluster or not
        self.modify_cluster = modify_cluster

        if self.modify_cluster:
            argo_namespace = self.cfg['argo_cd']['argo']['namespace']
            subproc(['kubectl config set-context --current --namespace='
                     f'{argo_namespace}'])

        # this is state storage
        self.previous_app = ''

        # inital highlight if we got here via a link
        self.initial_app = highlighted_app

        # sensitive values we are prepared to take so far
        self.sensitive_values = {
                'cert_manager': {},
                'nextcloud': {},
                'home_assistant': {},
                'matrix': {},
                'mastodon': {},
                'postgres_operator': {},
                'zitadel': {}
                }

        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Compose app with for app input content
        """
        # header to be cute
        yield Header()

        # Footer to show keys
        footer = Footer()
        if not self.show_footer:
            footer.display = False
        yield footer

        full_list = []
        for app, app_meta in self.cfg.items():
            item = Selection(app.replace("_","-"), app, app_meta['enabled'])
            full_list.append(item)

        selection_list = SelectionList[str](*full_list,
                                            id='selection-list-of-apps')

        with Container(id="apps-config-container"):
            # top left: the SelectionList of k8s applications
            with Grid(id="left-apps-container"):
                yield selection_list

                with Grid(id="left-button-box"):
                    # yield AddAppInput()
                    yield ModifyAppGlobals()

            # top right: vertically scrolling container for all inputs
            yield VerticalScroll(id='app-inputs-pane')

            # Bottom half of the screen for select-apps
            with VerticalScroll(id="app-notes-container"):
                yield Label("", id="app-description")

    def on_mount(self) -> None:
        """
        screen and box border styling
        """
        self.title = "ʕ ᵔᴥᵔʔ smol-k8s-lab "
        sub_title = f"Apps Configuration for {self.app.current_cluster} (now with more 🦑)"
        self.sub_title = sub_title

        # select-apps styling - select apps container - top left
        select_apps_widget = self.get_widget_by_id("selection-list-of-apps")
        select_apps_widget.border_title = "[#ffaff9]♥[/] [i]select[/] [#C1FF87]apps"
        select_apps_widget.border_subtitle = "[@click=screen.launch_new_app_modal]✨ [i]new[/] [#C1FF87]app[/][/]"

        # if text to speech is on, read screen title
        self.call_after_refresh(self.app.play_screen_audio, screen="apps")

        # scroll down to specific app if requested
        if self.initial_app:
            self.scroll_to_app(self.initial_app)

    def action_try_next_screen(self) -> None:
        """
        verify all the apps fields are valid, and if not, launch a warning
        modal screen and don't allow continue to next screen

        if all apps fields are valid, try to launch the smol_k8s_cfg screen
        """
        def check_invalid_apps(app_field_tuple: tuple = None):
            """
            process the app we get back scroll to it
            """
            if app_field_tuple:
                app = app_field_tuple[0]
                # field = app_field[1]
                self.scroll_to_app(app)

        # go check all the apps for empty inputs
        invalid_apps = self.check_for_invalid_inputs(self.app.cfg['apps'])

        if invalid_apps:
            self.app.push_screen(InvalidAppsModalScreen(invalid_apps),
                                 check_invalid_apps)
        else:
            # save our sensitive values temporarily at the app level
            self.app.sensitive_values = self.sensitive_values
            self.app.action_request_smol_k8s_cfg()

    def check_for_invalid_inputs(self, apps_dict: dict = {}) -> list:
        """
        check each app for any empty init or secret key fields
        """
        invalid_apps = {}

        if apps_dict:
            for app, metadata in apps_dict.items():
                if not metadata['enabled']:
                    continue

                empty_fields = []

                # check for empty init fields (some apps don't support init at all)
                init_dict = metadata.get('init', None)
                if init_dict:
                    # make sure init is enabled before checking
                    if init_dict['enabled']:
                        # regular yaml inputs
                        init_values = init_dict.get('values', None)
                        if init_values:
                            for key, value in init_values.items():
                                if not value:
                                    empty_fields.append(key)

                        # sensitive inputs
                        init_sensitive_values = init_dict.get('sensitive_values',
                                                              None)
                        if init_sensitive_values:

                            prompts = self.check_for_env_vars(app, metadata)
                            if prompts:
                                skip = False

                                # cert manager is special
                                if app == "cert_manager":
                                    solver = init_values['cluster_issuer_acme_challenge_solver']
                                    if solver == "http01":
                                        skip = True

                                for value in prompts:
                                    if not self.sensitive_values[app].get(value, ""):
                                        if not skip:
                                            empty_fields.append(value)

                # check for empty secret key fields (some apps don't have secret keys)
                secret_keys = metadata['argo'].get('secret_keys', None)
                if secret_keys:
                    for key, value in secret_keys.items():
                        if not value:
                            empty_fields.append(key)

                if empty_fields:
                    invalid_apps[app] = empty_fields

        return invalid_apps

    def check_for_env_vars(self, app: str, app_cfg: dict = {}) -> list:
        """
        check for required env vars and return list of dict and set:
            values found dict, set of values you need to prompt for
        """
        # keep track of a list of stuff to prompt for
        prompt_values = []

        env_vars = app_cfg['init']['sensitive_values']

        # provided there's actually any env vars to go get...
        if env_vars:
            # iterate through list of env vars to check
            for item in env_vars:
                # check env and self.sensitive_values
                value = environ.get(
                        "_".join([app.replace("-", "_").upper(), item]),
                        default=self.sensitive_values[app].get(item.lower(), ""))

                if not value:
                    # append any missing values to prompt_values
                    prompt_values.append(item.lower())

                self.sensitive_values[app][item.lower()] = value

        return set(prompt_values)

    def action_launch_new_app_modal(self) -> None:
        """
        action bound to a key for adding a new app to launch the new app modal
        screen.
        """
        def create_new_app_in_yaml(app_response):
            """
            after the new app modal screen is closed, if they didn't click cancel
            it returns the name of the app and description for us to create a new
            app in the yaml with.
            """
            app_name = app_response[0]
            app_description = app_response[1]

            if app_name and app_description:
                underscore_name = app_name.replace(" ", "_").replace("-", "_")

                # updates the base user yaml
                self.app.cfg['apps'][underscore_name] = {
                    "enabled": True,
                    "description": app_description,
                    "argo": {
                        "secret_keys": {},
                        "repo": "",
                        "path": "",
                        "revision": "",
                        "namespace": "",
                        "directory_recursion": False,
                        "project": {
                            "source_repos": [""],
                            "destination": {
                                "namespaces": ["argocd"]
                                }
                            }
                        }
                    }

                # adds selection to the app selection list
                apps = self.app.get_widget_by_id("selection-list-of-apps")
                apps.add_option(Selection(underscore_name.replace("_", "-"),
                                          underscore_name, True))

                # scroll down to the new app
                apps.action_last()

        self.app.push_screen(NewAppModalScreen(["argo-cd"]),
                             create_new_app_in_yaml)

    def scroll_to_app(self, app_to_highlight: str) -> None:
        """
        lets you scroll down to the exact app you need in the app selection list
        """
        # get the apps selection list
        apps = self.query_one(SelectionList)

        # get the app name for the highlighted index
        highlight_app = apps.get_option_at_index(apps.highlighted).value

        # while the highlighted app is not app_to_highlight, keep scrolling
        while highlight_app != app_to_highlight:
            apps.action_cursor_down()
            highlight_app = apps.get_option_at_index(apps.highlighted).value

    @on(SelectionList.SelectionHighlighted)
    def update_highlighted_app_view(self) -> None:
        selection_list = self.query_one(SelectionList)

        # only the highlighted index
        highlighted_idx = selection_list.highlighted

        # the actual highlighted app
        highlighted_app = selection_list.get_option_at_index(highlighted_idx).value

        if self.app.speak_on_focus:
            self.app.action_say(f"highlighted app is {highlighted_app}")

        # update the bottom app description to the highlighted_app's description
        blurb = format_description(self.cfg[highlighted_app]['description'])
        self.get_widget_by_id('app-description').update(blurb)

        # styling for the select-apps - configure apps container - right
        app_title = highlighted_app.replace("_", " ").title()
        app_cfg_title = f"🔧 [i]configure[/] parameters for [#C1FF87]{app_title}"
        app_inputs_pane = self.get_widget_by_id("app-inputs-pane")
        app_inputs_pane.border_title = app_cfg_title

        if self.previous_app != "":
            app_input = self.get_widget_by_id(f"{self.previous_app}-inputs")
            app_input.display = False

        try:
            app_input = self.get_widget_by_id(f"{highlighted_app}-inputs")
            app_input.display = True
        except NoMatches:
            app_metadata = self.cfg[highlighted_app]
            app_input = VerticalScroll(AppInputs(highlighted_app, app_metadata),
                                       id=f"{highlighted_app}-inputs",
                                       classes="single-app-inputs")
            self.get_widget_by_id("app-inputs-pane").mount(app_input)

        # select-apps styling - bottom
        app_desc = self.get_widget_by_id("app-notes-container")
        app_desc.border_title = f"📓 {app_title} [i]notes[/i]"

        self.previous_app = highlighted_app

        if self.modify_cluster and self.cfg[highlighted_app]['enabled']:
            app_inputs_pane.border_subtitle = (
                    "[@click=screen.sync_argocd_app]🔁 sync[/]"
                    )
        else:
            app_inputs_pane.border_subtitle = ""

    def action_sync_argocd_app(self) -> None:
        """
        syncs an existing Argo CD application
        """
        app = self.previous_app.replace("_","-")

        # default response
        severity = "warning"
        response = f"No Argo CD Application called [b]{app}[/b] could be found 😞"

        if check_if_argocd_app_exists(app):
            res = sync_argocd_app(app, spinner=False)

            if res:
                severity = "information"
                if isinstance(res, list):
                    response = "\n".join(res)
                else:
                    response = res
            else:
                response = "No response recieved from Argo CD sync... 🤔"

        # if result is not valid, notify the user why
        self.notify(response,
                    timeout=10,
                    severity=severity,
                    title="🦑 Argo CD Sync Response\n")

    @on(SelectionList.SelectionToggled)
    def update_selected_apps(self, event: SelectionList.SelectionToggled) -> None:
        """
        when a selection list item is checked or unchecked, update the base app yaml
        """
        selection_list = self.query_one(SelectionList)
        app = selection_list.get_option_at_index(event.selection_index).value
        if app in selection_list.selected:
            self.app.cfg['apps'][app]['enabled'] = True
        else:
            self.app.cfg['apps'][app]['enabled'] = False

        self.app.write_yaml()
