import datetime
import time

import paho.mqtt.client as mqtt
import ssl


def connect_to_m1() -> mqtt.Client:
    # mytransport = 'websockets' # or 'tcp'
    mytransport = 'tcp'

    client = mqtt.Client(client_id="paho-mqtt-test",
                         transport=mytransport,
                         protocol=mqtt.MQTTv5)

    user = "labtest"
    password = "labtest"
    client.username_pw_set(user, password)
    #TODO: when I get TLS working, use certificates instead
    # client.tls_set(certfile=None,
    #                keyfile=None,
    #                cert_reqs=ssl.CERT_REQUIRED)

    client.on_message = on_message
    client.on_connect = connect_callback
    # client.on_publish = mycallbacks.on_publish
    # client.on_subscribe = mycallbacks.on_subscribe

    broker = 'm1' # eg. choosen-name-xxxx.cedalo.cloud
    myport = 1883

    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes

    properties=Properties(PacketTypes.CONNECT)
    properties.SessionExpiryInterval=30*60 # in seconds
    client.connect(broker,
                   port=myport,
                   clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                   properties=properties,
                   keepalive=60)

    return client

def publish(client, payload, qos, topic):
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes
    properties = Properties(PacketTypes.PUBLISH)
    properties.MessageExpiryInterval = 30  # in seconds
    client.publish(topic, payload, qos, properties=properties)


def on_message(client, userdata, message,tmp=None):
    print(" Received message " + str(message.payload)
        + " on topic '" + message.topic
        + "' with QoS " + str(message.qos))


def connect_callback(client, userdata, flags, reasonCode, properties):
    print(f" Connected userdata:{userdata} flags:{flags} reason:{reasonCode} props:{properties}")

def main():

    client = connect_to_m1()
    topic = "test/doug-paho-test"

    payload = f"The time is currently {datetime.datetime.now()}"
    qos = 2

    print("DBNote: publishing")
    publish(client, payload, qos, topic)
    client.subscribe(topic, qos)

    print("DBNote: starting loop")
    retval = client.loop_start()

    print("DBNote: sleeping")
    time.sleep(5)

    print("DBNote: done")



if __name__ == '__main__':
    main()

