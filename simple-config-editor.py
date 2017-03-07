#!/usr/bin/env python3
"""
merge a config change and commit it.

Requires config.cfg with your config snippet inside at root directory.
"""
from jnpr.junos import Device
from iptools import ipv4
import getpass
import argparse

def make_changes(device, config_file):
    """
    If all has gone well up to here, you may want to merge the config or
    discard it.
    """
    # merge the local config snip
    # compare the config. If there is no diff, exit and move to next switch or
    # exit.
    if (device.compare_config()): #device is napalm
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


def open_device(device_ip, creds_dict):
    #do this with pyez instead of napalm
    """
    Helper function to try all creds on each device. Returns an open device or
    None if all creds fail.
    """
    print("Trying ".format(device_ip))
    for _user, _password in creds_dict.items():
        _device = Device(device_ip, user=_user, passwd=_password)
        _count = 0
        try:
            _device.open()
            return _device
        except Exception:
            # retry with available credentials until list is exhausted
            # if no credentials work, log an error.
            _count += 1
            print("Failed {0} out of {0} login attempts...".format(_count,
                  len(creds_dict)))
        print(_device)


def main(default="config.cfg", username="user", password="password",
         switch="switch.cfg"):
    # Do this with pyez instead of napalm.
    """Open the device, merge the config and commit it."""
    _device = open_device(switch, {username: password})
    print(_device.facts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('--config', type=str, help='path to file with config'
                        ' snippet.')
    parser.add_argument('--switch', type=str, help='Either a single IP address'
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
    elif args.creds_file:
        try:
            _creds_file = open(args.creds_file, 'r')
        except Exception:
            raise
        for _line in _creds_file:
            #Does this make sense for a creds file with more than one entry?
            username, password = _line.split(" ")
            password.rstrip()

    if ipv4.validate_ip(args.switch): # These cases are redundant. reduce this code!!
        try:
            main(args.config, args.user, password, switch_ip.rstrip())
        except Exception as e:
            print("There was a problem connecting to {}".format(switch_ip) + str(e))
    elif args.switch:
        # get list of switches from the file and iterate through them.
        try:
            switch_list_file = open(switch_ip, 'r')
        except Exception:
            raise
        print(switch_ip)
        for ip_addr in switch_list_file:
            try:
                print(ip_addr)
                main(args.config, args.user, password, ip_addr.rstrip())
            except ConnectionFailure:
                print("There was a problem connecting to {}".format(ip_addr))
    else:
        raise ConnectionFailure
