#!/usr/bin/env python3
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


def make_changes(device):
    """
    If all has gone well up to here, you may want to merge the config or
    discard it.
    """
    #merge the local config snip
    device.load_merge_candidate(filename=default)
    # compare the config. If there is no diff, exit and move to next switch or
    # exit.
    commit_result = device.commit_config()


def open_device(device_ip, driver, creds_dict):
    """
    Helper function to try all creds on each device.
    returns an open device or None if all creds fail.
    """

    for _user, _password in creds_dict.iteritems():
        print(_user + " " + _password)
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

    if ipv4.validate_ip(switch):
        # It's a single IP address, act on it and quit.
        creds_dict = {username: password}
        device = open_device(switch, driver, creds_dict)

        if device:
            device.close()
            print("Device is closed")
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
