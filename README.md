# simple-config-editor
Network automation script for Juniper devices. This is meant to take a list of switches and a list of credential pairs and apply a configuration snippet to the listed switches.

This script requires a config file with .set extension and config statements in "set" format. For example, you could have a file named config.set with the following contents:

    set system services ssh root-login deny
    set system services netconf ssh

