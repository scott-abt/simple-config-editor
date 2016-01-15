#!/usr/bin/env python
"""
merge a config change and commit it.

Requires config.cfg with your config snippet inside at root directory.
"""
from napalm import get_network_driver
from jnpr.junos.exception import ConnectAuthError
from iptools import ipv4
import os
import getpass
import argparse


def make_changes(device, config_file):
    """
    If all has gone well up to here, you may want to merge the config or
    discard it.
    """
    # merge the local config snip
    device.load_merge_candidate(filename=config_file)
    # compare the config. If there is no diff, exit and move to next switch or
    # exit.
    if (device.compare_config()):
        commit_answer = "n"
        print(device.compare_config())
        commit_answer = raw_input("Do you want to commit the changes? (y/N)")
        if commit_answer is "y":
            commit_result = device.commit_config()
            print(commit_result)
        else:
            print("Rolling back to active configuration... ")
            device.discard_config()
    else:
        print("There is no difference.")

def open_device(device_ip, driver, creds_dict):
    """
    Helper function to try all creds on each device.
    returns an open device or None if all creds fail.
    """

    for _user, _password in creds_dict.iteritems():
        _device = driver(device_ip, _user, _password)
        _count = 0
        try:
            _device.open()
            return _device
        except ConnectAuthError as cae:
            # retry with available credentials until list is exhausted
            # if no credentials work, log an error.
            _count += 1
            print("Failed {0} out of {0} login attempts...".format(_count,
                    len(creds_dict)))
            continue
    return None


def main(default="config.cfg", username="user", password="password",
         switch="switch.conf"):
    """Open the device, merge the config and commit it."""
    driver = get_network_driver('junos')

    # User could have passed an IP address or a path to a file in "switch"
    if ipv4.validate_ip(switch):
        # It's a single IP address, act on it and quit.
        creds_dict = {username: password}
        device = open_device(switch, driver, creds_dict)

        if device:
            make_changes(device, default)
            device.close()
            print("{0} is closed".format(device.hostname))
        else:
            print("Sionara!")
    elif os.path.exists(switch):
        # it's potentially a path to a file. Check that out
        print("It's a file, Jim.")
    else:
        print("It's not either of those things.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('config', type=str, help='path to file with config'
                        ' snippet.')
    parser.add_argument('user', type=str, help='Username with access to the'
                        ' switch(es).')
    parser.add_argument('switch', type=str, help='Either a single IP address'
        ' in X.X.X.X format, or a path to a file containing a list of switch IP'
        ' addresses 1 per line.')

    args = parser.parse_args()

    password = getpass.getpass()


    main(args.config, args.user, password, args.switch)
