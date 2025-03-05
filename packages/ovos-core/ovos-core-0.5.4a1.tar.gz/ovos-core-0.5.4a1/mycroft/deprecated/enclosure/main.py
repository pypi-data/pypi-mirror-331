# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
NOTE: this is dead code! do not use!

This file is only present to ensure backwards compatibility
in case someone is importing from here

This is only meant for 3rd party code expecting ovos-core
to be a drop in replacement for mycroft-core

"""

from ovos_config.locale import setup_locale
from ovos_config.config import Configuration
from ovos_gui.service import GUIService
from ovos_utils.log import LOG
from ovos_utils import wait_for_exit_signal
from ovos_utils.process_utils import reset_sigint_handler


def on_ready():
    LOG.info("Enclosure started!")


def on_stopping():
    LOG.info('Enclosure is shutting down...')


def on_error(e='Unknown'):
    LOG.error(f'Enclosure failed: {e}')


def create_enclosure(platform):
    """Create an enclosure based on the provided platform string.

    Args:
        platform (str): platform name string

    Returns:
        Enclosure object
    """
    if platform == "mycroft_mark_1":
        LOG.info("Creating Mark I Enclosure")
        LOG.warning("'mycroft_mark_1' enclosure has been deprecated!\n"
                    "'mark_1' support is being migrated into PHAL\n"
                    "see https://github.com/OpenVoiceOS/ovos_phal_mk1")
        from mycroft.deprecated.enclosure.mark1 import EnclosureMark1
        enclosure = EnclosureMark1()
    elif platform == "mycroft_mark_2":
        LOG.info("Creating Mark II Enclosure")
        LOG.warning("'mycroft_mark_2' enclosure has been deprecated!\n"
                    "It was never implemented outside the mk2 feature branch\n"
                    "mark_2 support is being migrated into PHAL\n"
                    "see https://github.com/OpenVoiceOS/ovos_phal_mk2")
        from mycroft.deprecated.enclosure.mark2 import EnclosureMark2
        enclosure = EnclosureMark2()
    else:
        LOG.info("Creating generic enclosure, platform='{}'".format(platform))
        from mycroft.deprecated.enclosure.generic import EnclosureGeneric
        enclosure = EnclosureGeneric()

    return enclosure


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping):
    """Launch one of the available enclosure implementations.

    This depends on the configured platform and can currently either be
    mycroft_mark_1 or mycroft_mark_2, if unconfigured a generic enclosure will be started.

    NOTE: in ovos-core the GUI protocol is handled in it's own service and not part of the enclosure like in mycroft-core!
          You need to also run mycroft.gui process separately, it has been extracted into it's own module
    """
    # Read the system configuration
    config = Configuration()

    LOG.warning("mycroft.client.enclosure is DEPRECATED in ovos-core!")
    LOG.warning("see https://github.com/OpenVoiceOS/ovos_PHAL")

    if not config.get("backwards_compat", True):
        raise DeprecationWarning("Please run PHAL instead of enclosure")

    reset_sigint_handler()
    setup_locale()

    platform = config.get("enclosure", {}).get("platform")

    if platform == "PHAL":
        LOG.debug("Launching PHAL")
        # config read from mycroft.conf
        # "PHAL": {
        #     "ovos-PHAL-plugin-display-manager-ipc": {"enabled": true},
        #     "ovos-PHAL-plugin-mk1": {"enabled": True}
        # }
        try:
            from ovos_PHAL import PHAL
            phal = PHAL()
            phal.start()
            wait_for_exit_signal()
        except Exception as e:
            LOG.exception("PHAL failed to launch!")
            error_hook(e)
    else:
        enclosure = create_enclosure(platform)
        if enclosure:
            LOG.debug("Enclosure created")
            try:
                enclosure.run()
                ready_hook()
            except Exception as e:
                error_hook(e)
        else:
            LOG.info("No enclosure available for this hardware, running headless")

        LOG.warning("Backwards compatibility is enabled, attempting to launch gui service...")
        LOG.warning("Please run PHAL + gui service as separate processes instead!")
        try:
            service = GUIService()
            service.run()
        except Exception as e:
            LOG.error(f"GUI : {e}")
            service = None

        ready_hook()
        wait_for_exit_signal()

        if enclosure:
            enclosure.stop()
        if service:
            service.stop()
        stopping_hook()


if __name__ == "__main__":
    main()
