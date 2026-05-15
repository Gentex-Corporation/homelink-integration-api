from homelink.auth.abstract_auth import AbstractAuth
from homelink.auth.srp_auth import SRPAuth
from homelink.mqtt_provider import MQTTProvider
import asyncio
from aiohttp import ClientSession

USERNAME = ""
PASSWORD = ""


class AuthorizedSession(AbstractAuth):

    def __init__(self, session, srp_auth):
        super().__init__(session)
        self.srp_auth = srp_auth

    async def async_get_access_token(self):
        tokens = self.srp_auth.async_get_access_token(USERNAME, PASSWORD)
        return tokens["AuthenticationResult"]["AccessToken"]


def on_message(topic, message):
    print(topic, message)


async def main():
    async with ClientSession() as client:
        srp_auth = SRPAuth()
        auth_session = AuthorizedSession(client, srp_auth)
        provider = MQTTProvider(auth_session)

        provider.listen(on_message)
        print(await provider.enable())
        print(await provider.discover())

        while True:
            pass


if __name__ == "__main__":
    asyncio.run(main())
