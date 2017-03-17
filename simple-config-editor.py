#!/usr/bin/env python3
"""
merge a config change and commit it.

Requires config.set with your config snippet inside at root directory.
"""
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ProbeError, ConnectAuthError, CommitError, ConfigLoadError
from iptools import ipv4
import getpass
import argparse
import sys

def make_changes(device, config_file):
    """
    If all has gone well up to here, you may want to merge the config or
    discard it.
    """
    # merge the local config snip

    try:
        _config = Config(device, mode="exclusive")
        _config.load(path=config_file, merge=True)
    except ConfigLoadError as conferr:
        if (conferr.errs[0]["message"] == "statement not found"):
            pass
        else:
            raise

    print(_config)

    # compare the config. If there is no diff, exit and move to next switch or
    # exit.
    if (_config.diff()):
        # check for diff
        print(_config.diff())

        commit_answer = "n"
        commit_answer = input("Do you want to commit the changes? (y/N)")

        if commit_answer.lower() == "y":
            # call commit_check then commit
            try:
                _config.commit_check()
            except CommitError as ce:
                raise

            try:
                _config.commit(confirm=2)
                _config.commit(comment="Change performed via automation")
            except CommitError as ce:
                raise

        else:
            print("Rolling back to active configuration... ")
            _config.rollback(rb_id=0)
    else:
        print("There is no difference.")

def open_device(device_ip, creds_dict):
    """
    Helper function to try all creds on each device. Returns an open device or
    None if all creds fail.
    """
    print("Trying {}".format(device_ip))
    for _user, _password in creds_dict.items():
        _device = Device(device_ip, port=22, user=_user, passwd=_password, 
                         attempts=3, auto_probe=True)
        _count = 0
        try:
            _device.open()
            return _device
        except ProbeError as proberr:
            print(str(proberr) + " NetConf is not available")
        except ConnectAuthError as e:
            # retry with available credentials until list is exhausted
            # if no credentials work, log an error.
            _count += 1
            print("Failed {0} out of {0} login attempts...".format(_count,
                  len(creds_dict)))
            print(str(e) + " Incorrect username or password")
        sys.exit(1)

def main(config, username, password, switch):
    """Open the device, merge the config and commit it."""
    _device = open_device(switch, {username: password})
    print(_device.facts)
    make_changes(_device, config)
    _device.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('--creds_file', type=str, help='File containing '
                        'list of credential pairs to try.')
    parser.add_argument('--user', type=str, help='Username with access '
                        'to the switch(es).')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--switch', type=str, help='Either a single IP address'
                        ' in X.X.X.X format, or a path to a file containing a'
                        ' list of switch IP addresses 1 per line.', required=True)
    required_args.add_argument('--config', type=str, required=True,
                               help='path to file with config snippet.')

    args = parser.parse_args()

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
        main(args.config, args.user, password, args.switch.rstrip())
    else:
        # get list of switches from the file and iterate through them.
        try:
            switch_list_file = open(args.switch, 'r')
        except Exception:
            raise
        print(args.switch)
        for ip_addr in switch_list_file:
            try:
                print(ip_addr)
                main(args.config, args.user, password, ip_addr.rstrip())
            except ConnectionFailure:
                print("There was a problem connecting to {}".format(ip_addr))
