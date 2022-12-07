"""
Using Textualize's rich library to pretty print subprocess outputs,
so during long running commands, the user isn't wondering what's going on,
even if you don't actually output anything from stdout/stderr of the command.
"""

import logging as log
from subprocess import Popen, PIPE
from rich.console import Console
from rich.theme import Theme


soft_theme = Theme({"info": "dim cornflower_blue",
                    "warn": "bold black on yellow",
                    "danger": "bold magenta"})
console = Console(theme=soft_theme)


def basic_syntax(bash_string=""):
    """
    splits up a string and does some basic syntax highlighting
    """
    parts = bash_string.split(' ')
    base_cmd = f'[magenta]{parts[0]}[/magenta]'
    if len(parts) == 1:
        return base_cmd
    else:
        bash_string = bash_string.replace(parts[0], base_cmd)
        bash_string = bash_string.replace(parts[1],
                                          f'[yellow]{parts[1]}[/yellow]')
        return bash_string


def subproc(commands=[], **kwargs):
    """
    Takes a list of command strings to run in subprocess
    Optional vars - default, description:
        error_ok        - catch Exceptions and log them, default: False
        quiet           - don't output from stderr/stdout, Default: False
        spinner         - show an animated progress spinner. can break sudo
                          prompts and should be turned off. Default: True
        cwd             - path to run commands in. Default: pwd of user
        shell           - use shell with subprocess or not. Default: False
        env             - dictionary of env variables for BASH. Default: None
    """
    # get/set defaults and remove the 2 output specific args from the key word
    # args dict so we can use the rest to pass into subproc.Popen later on
    spinner = kwargs.pop('spinner', True)
    quiet = kwargs.get('quiet', False)

    if spinner:
        # only need this if we're doing a progress spinner
        console = Console()

    for cmd in commands:

        # do some very basic syntax highlighting
        printed_cmd = basic_syntax(cmd)
        if not quiet:
            status_line = "[green] Running:[/green] "

            # make sure I'm not about to print a password, oof
            if 'password' not in cmd.lower():
                status_line += printed_cmd
            else:
                status_line += printed_cmd.split('assword')[0] + \
                    'assword[warn]:warning: TRUNCATED'
        else:
            cmd_parts = printed_cmd.split(' ')
            msg = '[green]Running [i]secret[/i] command:[b] ' + cmd_parts[0]
            status_line = " ".join([msg, cmd_parts[1], '[dim]...'])
        status_line += '\n'

        log.info(status_line, extra={"markup": True})

        # Sometimes we need to not use a little loading bar
        if not spinner:
            output = run_subprocess(cmd, **kwargs)
        else:
            with console.status(status_line,
                                spinner=spinner,
                                speed=0.75) as status:
                output = run_subprocess(cmd, **kwargs)

    return output


def run_subprocess(command, **kwargs):
    """
    Takes a str commmand to run in BASH in a subprocess.
    Typically run from subproc, which handles output printing.
    error_ok=False, directory="", shell=False
    Optional keyword vars:
        error_ok  - bool, catch errors, defaults to False
        cwd       - str, current working dir which is the dir to run command in
        shell     - bool, run shell or not
        env       - environment variables you'd like to pass in
    """
    # get the values if passed in, otherwise, set defaults
    quiet = kwargs.pop('quiet', False)
    error_ok = kwargs.pop('error_ok', False)

    log.debug(command)
    log.debug(kwargs)
    try:
        p = Popen(command.split(), stdout=PIPE, stderr=PIPE, **kwargs)
        res = p.communicate()
    except Exception as e:
        if error_ok and not quiet:
            log.error(str(e))

    return_code = p.returncode
    res_stdout, res_stderr = res[0].decode('UTF-8'), res[1].decode('UTF-8')
    if not quiet:
        log.info(res_stdout)

    # check return code, raise error if failure
    if not return_code or return_code != 0:
        # also scan both stdout and stdin for weird errors
        for output in [res_stdout.lower(), res_stderr.lower()]:
            if 'error' in output:
                err = f'Return code: "{str(return_code)}". Expected code is 0.'
                error_msg = f'\033[0;33m{err}\n{output}\033[00m'
                if error_ok:
                    if not quiet:
                        log.error(error_msg)
                else:
                    raise Exception(error_msg)

    # sometimes stderr is empty, but sometimes stdout is empty
    for output in [res_stdout, res_stderr]:
        if output:
            return output
