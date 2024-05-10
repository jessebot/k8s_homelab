from smol_k8s_lab.k8s_tools.backup import create_pvc_restic_backup
from smol_k8s_lab.utils.value_from import extract_secret
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Grid, Container
from textual.validation import Length
from textual.widgets import Input, Label, Static, Switch, Collapsible, Button
from textual.worker import get_current_worker


class BackupWidget(Static):
    """
    a textual widget for backing up select apps via k8up
    """

    def __init__(self,
                 app_name: str,
                 backup_params: dict,
                 cnpg_restore: bool,
                 id: str) -> None:
        self.app_name = app_name
        self.backup_params = backup_params
        self.cnpg_restore = cnpg_restore
        self.backup_s3_bucket = backup_params['s3']['bucket']
        self.backup_s3_endpoint = backup_params['s3']['endpoint']
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Grid(classes="backup-button-grid",
                   id=f"{self.app_name}-backup-button-grid")

        yield Label("⏲ Scheduled backups", classes="header-row")
        # first put in the schedule
        argo_label = Label("PVC schedule:", classes="argo-config-label")
        argo_label.tooltip = "schedule for recurring backup, takes cron syntax"
        input_id = f"{self.app_name}-backup-schedule"
        schedule_val = self.backup_params.get('schedule', "0 0 * * *")
        input = Input(placeholder="Enter a cron syntax schedule for backups",
                      value=schedule_val,
                      name='cron syntax schedule',
                      validators=[Length(minimum=5)],
                      id=input_id,
                      classes=f"{self.app_name} argo-config-input")
        input.validate(schedule_val)
        yield Horizontal(argo_label, input, classes="argo-config-row")


        # Collapsible with grid for backup values
        yield Collapsible(
                Grid(classes="collapsible-updateable-grid",
                     id=f"{self.app_name}-backup-grid"),
                id=f"{self.app_name}-backup-config-collapsible",
                title="S3 Configuration",
                classes="collapsible-with-some-room",
                collapsed=False
                )

    def on_mount(self) -> None:
        """
        add button and generate all the backup option input rows
        """

        button = Button("💾 Backup Now",
                        classes="backup-button",
                        id=f"{self.app_name}-backup-button")
        button.tooltip = f"Press to perform a one-time backup of {self.app_name}"
        grid = self.get_widget_by_id(f"{self.app_name}-backup-button-grid")
        grid.mount(button)

        self.generate_s3_rows()

    def generate_s3_rows(self) -> None:
        """
        generate each row for the backup widget
        """
        grid = self.get_widget_by_id(f"{self.app_name}-backup-grid")

        # create a label and input row for each argo value, excedpt directory_recursion
        for key, value in self.backup_params['s3'].items():
            argo_label = Label(f"{key.replace('_',' ')}:",
                               classes="argo-config-label")
            argo_label.tooltip = value
            input_id = f"{self.app_name}-backup-s3-{key}"
            if isinstance(value, str):
                input_val = value
                sensitive = False
            else:
                sensitive = True
                input_val = extract_secret(value)

            input = Input(placeholder=f"Enter a {key}",
                          value=input_val,
                          name=key,
                          validators=[Length(minimum=3)],
                          id=input_id,
                          password=sensitive,
                          classes=f"{self.app_name} argo-config-input")
            input.validate(input_val)

            grid.mount(Horizontal(argo_label, input, classes="argo-config-row"))

        # finally we need the restic repository password
        argo_label = Label("restic repo password:", classes="argo-config-label")
        argo_label.tooltip = "restic repository password for encrypting your backups"
        input_id = f"{self.app_name}-backup-restic-repository-password"
        input_val = extract_secret(self.backup_params['restic_repo_password'])

        input = Input(placeholder="Enter a restic repo password for your encrypted backups",
                      value=input_val,
                      name="restic_repo_password",
                      validators=[Length(minimum=5)],
                      id=input_id,
                      password=True,
                      classes=f"{self.app_name} argo-config-input")
        input.validate(input_val)

        grid.mount(Horizontal(argo_label, input, classes="argo-config-row"))

    @on(Input.Changed)
    def update_base_yaml_for_input(self, event: Input.Changed) -> None:
        """
        whenever any of our inputs change, we update the base app's saved config.yaml
        """
        input = event.input
        sensitive = input.password
        if not sensitive:
            if "s3" in input.name:
                self.app.cfg['apps'][self.app_name]['backups']['s3'][input.name] = input.value
            else:
                self.app.cfg['apps'][self.app_name]['backups'][input.name] = input.value
            self.app.write_yaml()
        else:
            self.log(f"saving special value for {input.name} to screen cache")
            self.screen.sensitive_values[self.app_name][input.name] = input.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        get pressed button and act on it
        """
        id = event.button.id
        if id == f"{self.app_name}-backup-button":
            self.trigger_backup()

    @work(thread=True, group="backup-worker")
    def trigger_backup(self) -> None:
        """
        run backup of an app in a thread so we don't lock up the UI
        """
        namespace = self.screen.cfg[self.app_name]['argo']['namespace']

        self.log(
                f"💾 kicking off backup for {self.app_name} in the {namespace}"
                f"namespace to the bucket: {self.backup_s3_bucket} at the "
                f" endpoint: {self.backup_s3_endpoint}."
                )
        worker = get_current_worker()
        if not worker.is_cancelled:
                self.app.call_from_thread(create_pvc_restic_backup,
                                          app=self.app_name,
                                          namespace=namespace,
                                          endpoint=self.backup_s3_endpoint,
                                          bucket=self.backup_s3_bucket,
                                          cnpg_backup=self.cnpg_restore)
                self.log(f"💾 backup of {self.app_name} has completed.")

class RestoreAppConfig(Static):
    """
    a textual widget for restoring select apps via k8up
    """

    def __init__(self,
                 app_name: str,
                 restore_params: dict,
                 id: str) -> None:
        self.app_name = app_name
        self.restore_params = restore_params
        self.cnpg_restore = restore_params.get("cnpg_restore", "not_applicable")
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        # verify restore is enabled
        restore_enabled = self.restore_params['enabled']

        # restore enabled label switch row
        with Container(classes=f"app-less-switch-row {self.app_name}"):
            # left hand side: base label with tool tip
            init_lbl = Label("Restore from backup", classes="initialization-label")
            init_lbl.tooltip = (
                "If enabled, smol-k8s-lab will [magenta]restore[/magenta] "
                f"{self.app_name}'s PVCs from an [b]s3[/b] compatible endpoint "
                "using [b]restic[/b] via [b]k8up[/b]. (Optionally, we can also "
                "restore a CNPG cluster)")
            yield init_lbl

            # right hand side: Enabled label and switch
            yield Label("Enabled: ", classes="app-init-switch-label")
            switch = Switch(value=restore_enabled,
                            id=f"{self.app_name}-restore-enabled",
                            name="restore enabled",
                            classes="app-init-switch")
            yield switch

        # cnpg operator restore enabled switch row
        if self.cnpg_restore != "not_applicable":
            cnpg_row = Container(classes=f"app-less-switch-row {self.app_name}",
                                 id=f"{self.app_name}-restore-cnpg-row")
            if not restore_enabled:
                cnpg_row.display = restore_enabled
            yield cnpg_row

        # Restic snapshot IDs collapsible, that gets hidden if restore
        # is disabled with switch above
        yield Label("Restic Snapshot IDs", classes="header-row",
                    id=f"{self.app_name}-snapshots-header")
        yield Grid(classes="collapsible-updateable-grid",
                   id=f"{self.app_name}-restore-grid")

    def on_mount(self) -> None:
        """
        add tool tip for collapsible and generate all the argocd input rows
        """
        header = self.get_widget_by_id(f"{self.app_name}-snapshots-header")
        header.tooltip = "Configure parameters for a restore from backups."

        # enable or disable cnpg restore if available
        if isinstance(self.cnpg_restore, bool):
            box = self.get_widget_by_id(f"{self.app_name}-restore-cnpg-row")
            init_lbl = Label("Restore CNPG cluster", classes="initialization-label")
            init_lbl.tooltip = (
                    "if supported, smol-k8s-lab will perform a one-time initial"
                    f" restore of this {self.app_name}'s CNPG cluster from an "
                    "s3 endpoint using [b]barman[/b]"
                    )
            box.mount(init_lbl)
            box.mount(Label("Enabled: ", classes="app-init-switch-label"))
            box.mount(Switch(value=self.cnpg_restore,
                             id=f"{self.app_name}-cnpg-restore-enabled",
                             name="cnpg restore enabled",
                             classes="app-init-switch"))

        if self.restore_params.get("restic_snapshot_ids", None):
            self.generate_snapshot_id_rows()

    def generate_snapshot_id_rows(self,) -> None:
        """
        generate each row of snapshot ids for the restore widget
        """
        grid = self.get_widget_by_id(f"{self.app_name}-restore-grid")
        # create a label and input row for each restic snapshot ID
        for key, value in self.restore_params["restic_snapshot_ids"].items():
            if not value:
                value = "latest"

            argo_label = Label(f"{key.replace('_',' ')}:", classes="argo-config-label")
            argo_label.tooltip = f"restic snapshot ID for {self.app_name} {key}"
            if self.app_name in key:
                input_id = f"{key}-restic-snapshot-id"
            else:
                input_id = f"{self.app_name}-{key}-restic-snapshot-id"
            input = Input(placeholder=f"Enter a {key}",
                          value=value,
                          name=key,
                          validators=[Length(minimum=3)],
                          id=input_id,
                          classes=f"{self.app_name} argo-config-input")
            input.validate(value)

            grid.mount(Horizontal(argo_label, input, classes="argo-config-row"))

    @on(Input.Changed)
    def update_base_yaml_for_input(self, event: Input.Changed) -> None:
        """
        whenever any of our inputs change, we update the base app's saved config.yaml
        """
        input = event.input
        parent_app_yaml = self.app.cfg

        parent_app_yaml['apps'][self.app_name]['init']['restore']['restic_snapshot_ids'][input.name] = input.value

        self.app.write_yaml()

    @on(Switch.Changed)
    def update_base_yaml_for_switch(self, event: Switch.Changed) -> None:
        """
        if user changes the restore enabled value, we write that out
        and we display or hide the restic values based on that
        """
        truthy = event.value

        if event.switch.id == f"{self.app_name}-restore-enabled":
           grid = self.get_widget_by_id(f"{self.app_name}-restore-config-collapsible")
           grid.display = truthy
           restore_row = self.get_widget_by_id(f"{self.app_name}-restore-cnpg-row")
           restore_row.display = truthy

           self.app.cfg['apps'][self.app_name]['init']['restore']['enabled'] = truthy
           self.app.write_yaml()

        if event.switch.id == f"{self.app_name}-cnpg-restore-enabled":
           self.app.cfg['apps'][self.app_name]['init']['restore']['cnpg_restore'] = truthy
           self.app.write_yaml()
