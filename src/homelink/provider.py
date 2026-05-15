import json
import logging

from homelink.auth.abstract_auth import AbstractAuth
from homelink.model.button import Button
from homelink.model.device import Device
from homelink.settings import DISCOVER_URL, ENABLE_URL


class Provider:
    def __init__(self, authorized_session):
        self.authorized_session = authorized_session

    async def discover(self):
        resp = await self.authorized_session.request(
            "POST",
            DISCOVER_URL,
            json={"command": "DISCOVER"},
        )
        device_data = await resp.json()
        logging.info(device_data)
        devices = []

        for raw_device in device_data["data"]["devices"]:
            d = Device(raw_device["id"], raw_device["name"])
            for raw_button in raw_device["buttons"]:
                d.buttons.append(Button(raw_button["id"], raw_button["name"], d))
            devices.append(d)

        return devices

    async def enable(self):
        enable_resp = await self.authorized_session.request(
            "POST",
            ENABLE_URL,
            json={"command": "ENABLE"},
        )
        return await enable_resp.json()
