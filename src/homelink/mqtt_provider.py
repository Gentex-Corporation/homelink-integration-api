import logging

from homelink.model.button import Button
from homelink.model.device import Device
from homelink.settings import DISCOVER_URL, ENABLE_URL, MQTT_IOT_ENDPOINT, MQTT_IOT_PORT

import paho.mqtt.client as mqtt
import homelink.mqtt_util as mqtt_util
import ssl
import json
import tempfile
import os
import aiofiles
import asyncio


class MQTTProvider:
    def __init__(self, authorized_session):
        self.authorized_session = authorized_session
        self.mqtt_client = None
        self.listeners = []

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

    async def enable(self, sslContext=None):
        asyncio_loop = asyncio.get_running_loop()
        pkey, csr = await mqtt_util.generate_csr()
        _, pk_file_path = tempfile.mkstemp()
        async with aiofiles.open(pk_file_path, "wb") as f:
            await f.write(pkey)
        enable_resp = await self.authorized_session.request(
            "POST",
            ENABLE_URL,
            json={"command": "ENABLE", "data": {"csr": csr}},
        )

        resp_json = await enable_resp.json()
        f, cert_file_path = tempfile.mkstemp(text=True)
        async with aiofiles.open(cert_file_path, "w") as f:
            await f.write(resp_json["data"]["certificatePem"])

        topic = None
        topics = []
        try:
            topic = resp_json["data"]["topic"]
        except KeyError:
            pass

        try:
            topics = resp_json["data"]["topics"]
        except KeyError:
            pass

        self.mqtt_client = mqtt.Client(client_id="TODO", protocol=mqtt.MQTTv5)
        self.mqtt_client.user_data_set(
            {"topics": list(dict.fromkeys(topics, topic)), "listeners": self.listeners}
        )

        if sslContext:
            await asyncio_loop.run_in_executor(
                None, sslContext.load_cert_chain, cert_file_path, pk_file_path, None
            )
            await asyncio_loop.run_in_executor(
                None, sslContext.load_verify_locations, cert_file_path
            )
            self.mqtt_client.tls_set_context(sslContext)
        else:
            self.mqtt_client.tls_set(
                certfile=cert_file_path,
                keyfile=pk_file_path,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_connect_fail = self._on_connect_fail
        self.mqtt_client.on_disconnect = self._on_disconnect

        self.mqtt_client.connect(MQTT_IOT_ENDPOINT, MQTT_IOT_PORT, keepalive=60)
        self.mqtt_client.loop_start()

        os.remove(cert_file_path)
        os.remove(pk_file_path)

        return resp_json

    async def disable(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        enable_resp = await self.authorized_session.request(
            "POST", ENABLE_URL, json={"command": "DISABLE"}
        )
        return await enable_resp.json()

    def listen(self, cb):
        self.listeners.append(cb)

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            for topic in userdata["topics"]:
                client.subscribe(topic, qos=1)
        else:
            raise ConnectionError("Failed to connect")

    def _on_message(self, client, userdata, msg):
        res = {}
        json_msg = json.loads(msg.payload.decode("utf-8"))
        if "state" in json_msg:
            res = {"type": "state", "data": json_msg["state"]}
        elif "requestSync" in json_msg:
            res = {"type": "requestSync", "data": json_msg["requestSync"]}
        else:
            raise ConnectionError("Unidentified message type recieved")
        for listener in userdata["listeners"]:
            listener(msg.topic, res)

    def _on_connect_fail(self, client, userdata):
        res = {"type": "connect_fail", "data": {}}
        for listener in userdata["listeners"]:
            listener("connect_fail", res)

    def _on_disconnect(self, client, userdata, reason_code, properties):
        res = {"type": "disconnect", "data": {"code": reason_code}}
        for listener in userdata["listeners"]:
            listener("disconnect", res)
