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

from ovos_config.config import Configuration
from ovos_bus_client.client import MessageBusClient
from mycroft.util import start_message_bus_client


class Enclosure:
    def __init__(self):
        # Load full config
        config = Configuration()
        self.lang = config['lang']
        self.config = config.get("enclosure")
        self.global_config = config

        # Create Message Bus Client
        self.bus = MessageBusClient()

    def run(self):
        """Start the Enclosure after it has been constructed."""
        # Allow exceptions to be raised to the Enclosure Service
        # if they may cause the Service to fail.
        start_message_bus_client("ENCLOSURE", self.bus)

    def stop(self):
        """Perform any enclosure shutdown processes."""
        pass
