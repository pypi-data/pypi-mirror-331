"""
Entry point
"""

import asyncio
import contextlib
import sys
import threading

from ... import __homepage__, __project_name__, application_setup, application_shutdown, errors
from ...utils import update
from . import commands, utils

import logging  # isort:skip
_log = logging.getLogger(__name__)


def main(args=None):
    sys.exit(_main(args))


def _main(args=None):
    cmd = None
    update_check_thread = None

    try:
        # Get CommandBase subclass. We need that to access user-provided configuration from files
        # and CLI arguments.
        cmd = commands.run(args)

        # Ugly hack.
        application_setup(cmd.config)

        # Find newer version in a background thread.
        update_check_thread = _UpgradeCheck(
            check_for_prerelease=(
                cmd.config['config']['main']['check_for_prerelease']
                or
                update.current_is_prerelease()
            ),
        )

        if utils.is_tty():
            _log.debug('Running in interactive mode')
            from .tui import TUI
            ui = TUI()
            exit_code = ui.run(cmd.jobs_active)
        else:
            exit_code = 1
            utils.print_stderr('Not a TTY.\nIf you really need headless mode, feel free to send me a feature request.')

        _log.debug('Main application exit code: %r', exit_code)

    # UI was terminated by user prematurely
    except KeyboardInterrupt as e:
        utils.print_stderr(e)
        return 1

    except (errors.UiError, errors.DependencyError, errors.ContentError) as e:
        utils.print_stderr(e)
        return 1

    except Exception as e:
        # Unexpected exception
        import traceback
        for line in traceback.format_exception(type(e), e, e.__traceback__):
            utils.print_stderr(line.strip())
        utils.print_stderr()

        # Exceptions from subprocesses should save their traceback.
        # See errors.DaemonProcessError.
        if hasattr(e, 'original_traceback'):
            utils.print_stderr(e.original_traceback)
            utils.print_stderr()

        utils.print_stderr(f'Please report the traceback above as a bug: {__homepage__}')
        return 1

    else:
        # Print last job's output to stdout for use in output redirection.
        # Ignore disabled jobs.
        if exit_code == 0 and cmd.main_job.output:
            utils.print_stdout('\n'.join(cmd.main_job.output))

        if update_check_thread and update_check_thread.message:
            utils.print_stderr(update_check_thread.message)

        return exit_code

    finally:
        if cmd is not None:
            # Cleanup cache, close HTTP session, etc.
            application_shutdown(cmd.config)


class _UpgradeCheck(threading.Thread):
    def __init__(self, *, check_for_prerelease=False):
        self._newer_version = None
        self._changelog = None
        self._check_for_prerelease = check_for_prerelease

        # daemon=True allows the application to exit if this thread is still
        # running. We don't want to wait for slow/unresponsive web servers.
        super().__init__(daemon=True)
        self.start()

    def run(self):
        with contextlib.suppress(errors.RequestError):
            self._newer_version = asyncio.run(self._get_newer_version())
            if self._newer_version:
                self._changelog = asyncio.run(self._get_changelog())

    async def _get_newer_version(self):
        if self._check_for_prerelease:
            return await update.get_newer_prerelease()
        else:
            return await update.get_newer_release()

    async def _get_changelog(self):
        if self._check_for_prerelease:
            return await update.get_latest_changelog()
        else:
            return await update.get_latest_release_changelog()

    @property
    def message(self):
        # If we found a newer version, assemble a notification message.
        if self._newer_version:
            msg = (
                '\n' + ('━' * 78) + '\n'
                + '\n'
                + '  \\O/\n'
                + f'   |     {__project_name__} {self._newer_version} has been released.\n'
                + '  / \\\n'
            )

            if self._changelog:
                msg += (
                    '\n'
                    + self._changelog
                    + '\n'
                )

            return msg
