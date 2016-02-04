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

class ConnectionFailure(Exception):
    pass


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
        print(device.compare_onfig())
        commit_answer = "n"
        commit_answer = raw_input("Do you want to commit the changes? (y/N)")
        if commit_answer.lower() == "y":
            commit_result = device.commit_config()
            print(commit_result)
        else:
            print("Rolling back to active configuration... ")
            device.discard_config()
    else:
        print("There is no difference.")


def open_device(device_ip, driver, creds_dict):
    """
    Helper function to try all creds on each device. Returns an open device or
    None if all creds fail.
    """
    print("Trying ".format(device_ip))
    for _user, _password in creds_dict.iteritems():
        _device = driver(device_ip, _user, _password)
        _count = 0
        try:
            _device.open()
            return _device
        except ConnectAuthError:
            # retry with available credentials until list is exhausted
            # if no credentials work, log an error.
            _count += 1
            print("Failed {0} out of {0} login attempts...".format(_count,
                  len(creds_dict)))
    raise ConnectionFailure


def main(default="config.cfg", username="user", password="password",
         switch="switch.cfg"):
    """Open the device, merge the config and commit it."""
    driver = get_network_driver('junos')
    creds_dict = {username: password}
    device = open_device(switch, driver, creds_dict)

    if device:
        make_changes(device, default)
        device.close()
        print("{0} is closed".format(device.hostname))
    else:
        print("Sionara!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('config', type=str, help='path to file with config'
                        ' snippet.')
    parser.add_argument('switch', type=str, help='Either a single IP address'
                        ' in X.X.X.X format, or a path to a file containing a'
                        ' list of switch IP addresses 1 per line.')
    parser.add_argument('--user', type=str, help='Username with access '
                        'to the switch(es).')
    parser.add_argument('--creds_file', type=str, help='File containing '
                        'list of credential pairs to try.')

    args = parser.parse_args()
    switch_ip = args.switch

    if args.user:
        password = getpass.getpass()
    elif args.creds_file and os.path.exists(args.creds_file):
        _creds_file = open(args.creds_file, 'r')
        for _line in _creds_file:
            username, password = _line.split(" ")
            password.rstrip()

    if ipv4.validate_ip(args.switch): # These cases are redundant. reduce this code!!
        try:
            main(args.config, args.user, password, switch_ip.rstrip())
        except ConnectionFailure:
            print("There was a problem connecting to {}".format(switch_ip))
    elif os.path.exists(args.switch):
        # get list of switches from the file and iterate through them.
        switch_list_file = open(switch_ip, 'r')
        print(switch_ip)
        for ip_addr in switch_list_file:
            try:
                print(ip_addr)
                main(args.config, args.user, password, ip_addr.rstrip())
            except ConnectionFailure:
                print("There was a problem connecting to {}".format(ip_addr))
    else:
        raise ConnectionFailure