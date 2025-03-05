import websocket
import json
import datetime
from dataclasses import dataclass


@dataclass
class File:
    id: int
    path: str
    content: str

    def from_json(json: dict):
        return File(
            json.get("data", {}).get("fid"),
            json.get("data", {}).get("path"),
            json.get("data", {}).get("buffer"),
        )


class ScaffoldSession:
    def __init__(self, ticket):

        self.host = "wss://sahara.au.edstem.org"
        self.ticket = ticket

        self.filesById = {}

        url = f"{self.host}/connect?ticket={self.ticket}"
        self.socket = websocket.WebSocketApp(
            url,
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, error: self.on_error(ws, error),
            on_close=lambda ws, status, msg: self.on_close(ws, status, msg),
            on_open=lambda ws: self.on_open(ws),
        )

    def send_msg(self, msg):
        self.socket.send(json.dumps(msg))

    def send_ping(self):
        self.send_msg(
            {
                "type": "ping",
                "data": {
                    "sequence": 0,
                    "timestamp": datetime.datetime.now().isoformat(),
                },
            }
        )

    def start(self):
        self.socket.run_forever()

    def has_unopened_files(self):
        for id, file in self.filesById.items():
            if file is None:
                return True

        return False

    def on_message(self, socket, data):
        msg = json.loads(data)
        # print(f"REPLAY: {msg}")

        msgType = msg.get("type")

        if msgType == "init":

            for file in msg.get("data", {}).get("files_open", []):
                fileId = file["id"]
                filepath = file["path"]
                if file["path"].endswith(".java"):
                    self.filesById[fileId] = None
                    self.send_msg(
                        {"type": "file_open", "data": {"path": filepath, "soft": False}}
                    )

        if msgType == "file_ot_init":

            file = File.from_json(msg)
            self.filesById[file.id] = file

        # if msgType not in ['file_ot_save', 'replay_update', 'client_leave']:
        # self.log.write(data + "\n")

        # self.send_ping()

        if not self.has_unopened_files():
            self.close()

    def on_open(self, socket):
        # print("REPLAY: opened")
        return

    def on_error(self, socket, error):
        print(error)

    def on_close(self, socket, close_status_code, close_msg):
        return

    def close(self):
        # print("closing!")
        self.socket.close()
