import signal
import threading
import time
from collections import defaultdict
from typing import Callable, Any, Dict, List

from paho.mqtt.client import Client, MQTTMessage, MQTTv5, MQTT_CLEAN_START_FIRST_ONLY

UserData = Any

import attr


class MQTTMessageHandler(Callable[[Client, UserData, MQTTMessage], None,]):

    def __call__(self, client: Client, user_data: UserData, message: MQTTMessage) -> None:
        ...


@attr.define
class PahoRunner:
    client: Client
    topic_handlers: Dict[str, List[MQTTMessageHandler]] = defaultdict(list)

    def __attrs_post_init__(self) -> None:
        self.client.on_message = self._on_message

    def subscribe(self, topic: str, handler: MQTTMessageHandler, qos: int = 2) -> None:
        handlers = self.topic_handlers[topic]
        if not handlers:
            self.client.subscribe(topic, qos)

        handlers.append(handler)

    def unsubscribe(self, topic: str, handler: MQTTMessageHandler) -> None:
        handlers = self.topic_handlers[topic]
        handlers.remove(handler)

    def run(self) -> None:

        keep_going = threading.Event()

        def signal_handler(sig, frame):
            print('Disconnecting client')
            self.client.disconnect()
            nonlocal keep_going
            keep_going.set()

        signal.signal(signal.SIGINT, signal_handler)

        # DBNote: not sure if there are other things we want this thread to do?
        self.client.loop_start()
        while not keep_going.isSet():
            self._publish()
            keep_going.wait(timeout=10)

    def _on_message(self, client: Client, user_data: UserData, message: MQTTMessage) -> None:
        handlers = self.topic_handlers[message.topic]
        if not handlers:
            # TODO do some thing better than this
            print(f"Received message on unhandled topic {message.topic}")

        for handler in handlers:
            handler(client, user_data, message)

    def _publish(self) -> None:
        from datetime import datetime
        for topic in self.topic_handlers.keys():
            self.client.publish(topic, f"the time is now {datetime.now()}")
            time.sleep(1)


def connect_to_m1() -> Client:
    my_transport = 'tcp'
    user = "labtest"
    password = "labtest"
    broker = 'm1'
    my_port = 1883

    client = Client(client_id="paho-mqtt-test",
                    transport=my_transport,
                    protocol=MQTTv5)

    client.username_pw_set(user, password)
    # TODO: when I get TLS working, use certificates instead
    # client.tls_set(certfile=None,
    #                keyfile=None,
    #                cert_reqs=ssl.CERT_REQUIRED)

    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes

    properties = Properties(PacketTypes.CONNECT)
    properties.SessionExpiryInterval = 30 * 60  # in seconds
    client.connect(broker,
                   port=my_port,
                   clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                   properties=properties,
                   keepalive=60)

    return client


@attr.define
class MyHandler(MQTTMessageHandler):
    handler_name: str

    def __call__(self, client: Client, user_data: UserData, message: MQTTMessage) -> None:
        print(f"{self.handler_name} received on topic {message.topic} payload:{message.payload}")


def main():

    client = connect_to_m1()
    runner = PahoRunner(client)

    handler_1 = MyHandler("BoBo")
    handler_2 = MyHandler("FooFoo")

    runner.subscribe("test/Bobo-only", handler_1)
    runner.subscribe("test/FooFoo-only", handler_2)
    runner.subscribe("test/everyone", handler_2)
    runner.subscribe("test/everyone", handler_1)

    runner.run()
    print("Exiting!")


if __name__ == '__main__':
    main()
