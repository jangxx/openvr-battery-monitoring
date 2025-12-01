from typing import Optional
import json

from websockets.asyncio.client import connect, ClientConnection

class OvrtIcon:
    pass


class OvrtNotifier:
    socket: Optional[ClientConnection] = None

    def __init__(self):
        pass

    async def connect(self):
        try:
            self.socket = await connect("ws://127.0.0.1:11450/api")
        except Exception as e:
            print(f"Failed to connect to OVRT: {e}")
            self.socket = None

    async def send_notification(self, title: str, body: str, icon: Optional[OvrtIcon] = None):
        if self.socket is None:
            await self.connect()

        if self.socket is not None:
            try:
                notification = {
                    "title": title,
                    "body": body,
                    "icon": None, # TODO
                }

                message = {
                    "messageType": "notification",
                    "json": json.dumps(notification),
                }

                await self.socket.send(json.dumps(message))
            except Exception as e:
                print(f"Failed to send notification to OVRT: {e}")
                self.socket = None