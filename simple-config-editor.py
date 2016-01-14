#!/usr/bin/env python3
"""
merge a config change and commit it.

Requires config.cfg with your config snippet inside at root directory.
"""
import getpass
from napalm import get_network_driver
from jnpr.junos.exception import ConnectAuthError


def main(default="config.cfg", username="user", password="password"):
    """Open the device, merge the config and commit it."""
    driver = get_network_driver('junos')

    device_ip = input("Device IP Address or DNS: ")
    device = driver(device_ip, username, password)

    try:
        device.open()
    except ConnectAuthError as cae:
        print("___________________\nCredentials were incorrect. Please"
            " re-enter credentials.")
        username, password = get_creds()


    #merge the local config snip
    device.load_merge_candidate(filename=default)

    # Add confirmation dialog here
    # Show the diff. If the diff is blank, say there are no changes and move
    # on.

    print(device.compare_config())
    
    commit_answer = "y"
    commit_answer = input("Commit? (Y/n): ")

    if (commit_answer == "y" or commit_answer == "Y"):
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
