#!/usr/bin/env python
"""
AWS OpsWorks SSH menu

Dependencies:
    boto3
    iterfzf
"""

import sys
import os
import pprint
import boto3
from iterfzf import iterfzf


def get_ow_stacks(client: boto3.client) -> dict:
    """
    Get a list of opsworks stacks
    """
    output = {}

    response: dict = client.describe_stacks()

    for stack in response["Stacks"]:
        output[stack["Name"]] = stack["StackId"]

    owstack = iterfzf(output)

    try:
        return output[owstack]
    except KeyError:
        exit(0)


def get_ow_instances(client: boto3.client, stack: str):
    """
    Get a list of opsworks instances in stack
    """
    instances = client.describe_instances(
        StackId=stack
        )["Instances"]

    return instances


def determine_user(os):
    """
    Determines the SSH user from the OS
    """
    # TODO: Implement this https://alestic.com/2014/01/ec2-ssh-username/
    os_map = {
        "Amazon Linux": "ec2-user",
        "ubuntu": "ubuntu"
        }

    return os_map[os]


def pick_ow_instance(instances):
    """
    Pick the opsworks instance you want to SSH into
    """
    # TODO: Handle cases with multiple instances with the same hostname
    ppr = pprint.PrettyPrinter(indent=4)

    choices = {}

    for instance in instances:
        try:
            choices[instance["Hostname"]] = {
                "ip": instance["PrivateIp"],
                "os": instance["ReportedOs"]["Name"],
            }
        except KeyError:
            ppr.pprint(instance)
            exit(1)

    return choices[iterfzf(choices)]


def main():
    """
    Main
    """
    # TODO: Caching?
    # TODO: Proper command line support
    # TODO: Default profiles
    # TODO: Config?
    # TODO: Proper error handling
    # TODO: Write a generator function that yields the private ip-s if none
    try:
        profile: str = sys.argv[1]
        region: str = sys.argv[2]
    except IndexError:
        sys.exit("Invalid amount of parameters")

    session = boto3.session.Session(
        profile_name=profile, region_name=region)

    client = session.client("opsworks")

    stack_id = get_ow_stacks(client)

    instance = pick_ow_instance(get_ow_instances(client, stack_id))
    connect_string = determine_user(instance["os"]) + "@" + instance["ip"]
    print("Attempting to SSH: " + connect_string)
    os.system("ssh " + connect_string)


if __name__ == "__main__":
    main()
