import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


opened_by_others = []


class DeliveringConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            "deliverymen_room", self.channel_name
        )

        self.send_opened_by_others_state_to_all()
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "deliverymen_room", self.channel_name
        )
        user = self.scope["user"]

        for opened_by in opened_by_others:
            if opened_by["user_id"] == user.id:
                opened_by_others.remove(opened_by)

        self.send_opened_by_others_state_to_all()

    def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]

        if data.pop("action") == "open":
            found = False

            for opened_by in opened_by_others:
                if opened_by["order_id"] == data["order_id"]:
                    found = True
                    break

            if not found:
                data["user_fullname"] = user.first_name + " " + user.last_name
                data["user_id"] = user.id
                opened_by_others.append(data)
                self.send_opened_by_others_state_to_all()
        else:
            for opened_by in opened_by_others:
                if opened_by["order_id"] == data["order_id"] and opened_by["user_id"] == user.id:
                    opened_by_others.remove(opened_by)
                    self.send_opened_by_others_state_to_all()
                    break

    def deliverymen_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))

    def send_opened_by_others_state_to_all(self):
        async_to_sync(self.channel_layer.group_send)(
            "deliverymen_room", {"type": "deliverymen_message", "message": opened_by_others}
        )
