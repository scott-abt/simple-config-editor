#!/usr/bin/env python3
"""merge a config change and commit it."""

import getpass
from napalm import get_network_driver


def main(default="config.cfg", username="user", password="password"):
    """Open the device, merge the config and commit it."""
    driver = get_network_driver('junos')
    device = driver('10.56.133.100', username, password)
    device.open()

    #merge the local config snip
    device.load_merge_candidate(filename=default)


if __name__ == "__main__":
    username = input("Username: ")
    password = getpass.getpass()
    main(username=username, password=password)
