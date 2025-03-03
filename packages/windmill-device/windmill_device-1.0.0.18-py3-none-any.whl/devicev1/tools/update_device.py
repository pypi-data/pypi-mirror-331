#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/3
# @Author  : zhoubohan
# @File    : update_device.py
"""
import os
from argparse import ArgumentParser

import bcelogger as logger
from devicev1.client.device_api import (
    UpdateDeviceRequest,
    parse_device_name,
    DeviceStatus,
)
from windmillclient.client.windmill_client import WindmillClient


def parse_args() -> ArgumentParser:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Device meta update utility")
    parser.add_argument(
        "--device_names",
        required=True,
        type=str,
        help="Comma-separated list of device names",
    )
    parser.add_argument(
        "--status",
        default=DeviceStatus.Connected.value,
        type=str,
        help="Status of the device",
    )
    return parser.parse_args()


def update_devices(args):
    """
    Update the device metadata.
    """
    windmill_endpoint = os.getenv("WINDMILL_ENDPOINT")
    org_id = os.getenv("ORG_ID")
    user_id = os.getenv("USER_ID")
    windmill_client = WindmillClient(
        endpoint=windmill_endpoint, context={"OrgID": org_id, "UserID": user_id}
    )
    device_names = args.device_names.split(",")
    status = args.status
    for dn in device_names:
        logger.info(f"Updating device {dn} with status {status}")
        # Update the device metadata here
        device_name = parse_device_name(dn)
        if device_name is None:
            logger.error(f"Device name {dn} is invalid")
            continue

        try:
            windmill_client.update_device(
                UpdateDeviceRequest(
                    workspace_id=device_name.workspace_id,
                    device_name=device_name.local_name,
                    device_hub_name=device_name.device_hub_name,
                    status=status,
                )
            )
        except Exception as e:
            logger.error(f"Failed to update device {dn}: {e}")
            continue


if __name__ == "__main__":
    update_devices(parse_args())
