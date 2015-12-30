#!/usr/bin/env python3
"""merge a config change and commit it."""

import getpass
from napalm import get_network_driver
from jnpr.junos.exception import ConnectAuthError


def main(default="config.cfg", username="user", password="password"):
    """Open the device, merge the config and commit it."""
    driver = get_network_driver('junos')
    device = driver('10.56.133.100', username, password)

    try:
        device.open()
    except ConnectAuthError as cae:
        print("___________________\nCredentials were incorrect. Please"
            " re-enter credentials.")
        username, password = get_creds()

    #merge the local config snip
    device.load_merge_candidate(filename=default)
    
    commit_result = device.commit_config()
    print(commit_result)

    device.close()


def get_creds():
    username = input("Username: ")
    password = getpass.getpass()
    return [username, password]


if __name__ == "__main__":
    username, password = get_creds()
    main(username=username, password=password)
