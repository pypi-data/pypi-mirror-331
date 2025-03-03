__version__ = "0.4.0"

import ssl
import time
import json
import paho.mqtt.client as mqtt
from abc import abstractmethod

from era.era_const import LOGO
from era.era_timer import Timer
from era.era_protocol import Protocol

def era_log(*args):
    print("[LOG]", *args)

def ticks_ms():
    return int(time.time() * 1000)

def sleep_ms(ms):
    time.sleep(ms // 1000)

class ERaError(Exception):
    pass

class RedirectError(Exception):
    def __init__(self, host, port):
        self.host = host
        self.port = port

class Connection(Protocol):
    client = None
    state = None
    info = {}

    def __init__(self, token, host = "mqtt1.eoh.io", port = 1883,
                 log = era_log):
        Protocol.__init__(self, token)
        self.token = token
        self.host = host
        self.port = port
        self.log = log

    def publish(self, topic, payload, qos = 0, retain = False):
        self.client.publish(topic, payload, qos, retain)
        self.log("Publish {} ({}): {}".format(topic, len(payload), payload))

    def subscribe(self, topic, qos = 0):
        self.client.subscribe(topic, qos)
        self.log("Subscribe topic {}, QoS {}".format(topic, qos))

    def _disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.client.connected_flag = False
        self.state = self.DISCONNECTED

    def on_connect(self, client, userdata, flags, rc):
        if (rc == 0):
            self.client.connected_flag = True
            self.log("Connect OK!")
        else:
            self.log("Connect FAIL, code =", rc)

    def on_disconnect(self, client, userdata, rc):
        self._disconnect()
        self.log("Disconnected, code =", rc)

    @abstractmethod
    def on_message(self, client, userdata, message):
        pass

    def set_will(self):
        lwt = self.lwt_write_msg()
        self.client.will_set(lwt["topic"], json.dumps(lwt["payload"]), qos = 1, retain = True)

    def publish_state(self):
        state = self.state_write_msg()
        self.publish(state["topic"], json.dumps(state["payload"]), qos = 1, retain = True)

    def publish_info(self):
        self.publish(self.get_topic_info(), json.dumps(self.info), qos = 1, retain = False)

    def authenticate(self):
        self.log("Authenticating device...")
        mqtt.Client.connected_flag = False
        self.state = self.AUTHENTICATING
        self.client = mqtt.Client(client_id = self.token, clean_session = True)
        self.set_will()
        self.client.username_pw_set(self.token, self.token)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port, keepalive = 60)

        # Wait verify
        self.client.loop_start()
        start_time = time.time()
        while (not self.client.connected_flag and
                self.state is self.AUTHENTICATING and
                time.time() - start_time <= 20):
            time.sleep(1)
        if not self.client.connected_flag:
            raise ERaError("Authenticating timeout")
        self.subscribe(self.topic_down.format(self.token), qos = 1)
        self.subscribe(self.topic_virtual_pin.format(self.token), qos = 1)
        self.publish_state()
        self.state = self.AUTHENTICATED
        self.log("Access granted")

    def connected(self):
        return True if self.state == self.AUTHENTICATED else False

class ERa(Connection, Timer):
    VPIN_MAX_NUM = 255

    events = {}

    def __init__(self, token, **kwargs):
        Connection.__init__(self, token, **kwargs)
        Timer.__init__(self, False)
        self.state = self.DISCONNECTED
        print(LOGO.format(__version__, "Python"))

    def on_message(self, client, userdata, message):
        self.log("Message {} ({}): {}".format(message.topic, len(message.payload),
                                              message.payload.decode("utf-8")))
        try:
            msg_type, msg_id, msg_data = self.parse_response(message.topic,
                                                             message.payload.decode("utf-8"))
            self.process(msg_type, msg_id, msg_data)
        except TypeError:
            pass
        except ValueError:
            pass

    def parse_config(self, msg_data):
        try:
            for value in msg_data.get("configuration", {}).get("arduino_pin", {}).get("devices", []):
                virtual_pins = value.get("virtual_pins", [])
                self.config.extend({k: v for k, v in val.items() if k in ["config_id", "pin_number"]} for val in virtual_pins)
        except KeyError:
            pass
        except ValueError:
            pass

    def process(self, msg_type, msg_id, msg_data):
        if msg_type == "virtual_pin":
            msg_args = list(msg_data.values())
            self.call_handler("{}{}".format(self.VPIN_WRITE, msg_id), int(msg_id), *msg_args)
        elif msg_type == "down":
            self.parse_config(msg_data)
        else:
            raise ERaError("Wrong message")

    def make_info(self):
        import uuid
        self.info["id"] = str(uuid.uuid4())
        self.info["version"] = __version__
        self.info["firmware_version"] = __version__
        self.info["plug_and_play"] = 0

    def connect(self):
        while not self.connected():
            if self.state == self.DISCONNECTED:
                try:
                    self.authenticate()
                    self.log("Registered events: {}".format(list(self.events.keys())))
                    self.call_handler(self.CONNECT_EVENT, self.info)
                    self.make_info()
                    self.publish_info()
                    return True
                except ERaError as e_err:
                    self.disconnect(e_err)
                    sleep_ms(self.TASK_PERIOD_RES)
                except RedirectError as r_err:
                    self.disconnect()
                    self.host = r_err.host
                    self.port = r_err.port
                    sleep_ms(self.TASK_PERIOD_RES)
                return False

    def disconnect(self, err_msg):
        self._disconnect()
        self.call_handler(self.DISCONNECT_EVENT)
        if err_msg:
            self.log("Disconnected: {}".format(err_msg))
        time.sleep(self.RECONNECT_SLEEP)

    def virtual_write(self, v_pin, value, **kwargs):
        data = self.virtual_write_msg(v_pin, ("v", value), **kwargs)
        if data:
            self.publish(data["topic"], json.dumps(data["payload"]), qos = 1, retain = True)

    def register_timer(era, *args, **kwargs):
        return Timer.register(era, *args, **kwargs)

    def register_handler(era, event_name):
        class Deco(object):
            def __init__(self, func):
                self.func = func
                if str(event_name).lower() in (era.VPIN_READ_ALL, era.VPIN_WRITE_ALL):
                    event_base_name = str(event_name).split(era.VPIN_WILDCARD)[0]
                    for i in range(era.VPIN_MAX_NUM + 1):
                        era.events["{}{}".format(event_base_name.lower(), i)] = func
                else:
                    era.events[str(event_name).lower()] = func

            def __call__(self):
                return self.func()

        return Deco

    def call_handler(self, event, *args, **kwargs):
        if event in self.events.keys():
            self.log("Event: ['{}'] -> {}".format(event, args))
            self.events[event](*args, **kwargs)

    def run(self):
        try:
            Timer.run(self)
            if not self.connected():
                self.connect()
        except KeyboardInterrupt:
            raise
        except OSError as o_err:
            self.log(o_err)
        except ERaError as e_err:
            self.disconnect(e_err)
        except Exception as g_exc:
            self.disconnect(g_exc)
