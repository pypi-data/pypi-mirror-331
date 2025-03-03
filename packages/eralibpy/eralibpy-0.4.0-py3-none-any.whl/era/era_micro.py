__version__ = "0.4.0"

try:
    import ussl as ssl
except ImportError:
    import ssl

import utime as time
import ujson as json
from micropython import const
from umqtt.simple import MQTTClient as mqtt

from era.era_const import LOGO
from era.era_timer import Timer
from era.era_protocol import Protocol

ticks_ms = time.ticks_ms
sleep_ms = time.sleep_ms

IOError = OSError

def era_log(*args):
    print("[LOG]", *args)

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
    last_ping_time = 0

    def __init__(self, token, host = "mqtt1.eoh.io", port = 1883,
                 keepalive = 60, log = era_log):
        Protocol.__init__(self, token)
        self.token = token
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self.log = log

    def publish(self, topic, payload, retain = False, qos = 0):
        self.last_ping_time = ticks_ms()
        self.client.publish(topic, payload, retain, qos)
        self.log("Publish {} ({}): {}".format(topic, len(payload), payload))

    def subscribe(self, topic, qos = 0):
        self.last_ping_time = ticks_ms()
        self.client.subscribe(topic, qos)
        self.log("Subscribe topic {}, QoS {}".format(topic, qos))

    def _disconnect(self):
        self.client.disconnect()
        self.state = self.DISCONNECTED

    def disconnect(self, err_msg = None):
        pass

    def on_message(self, topic, msg):
        pass

    def set_will(self):
        lwt = self.lwt_write_msg()
        self.client.set_last_will(lwt["topic"], json.dumps(lwt["payload"]), retain = True, qos = 1)

    def publish_state(self):
        state = self.state_write_msg()
        self.publish(state["topic"], json.dumps(state["payload"]), retain = True, qos = 1)

    def publish_info(self):
        self.publish(self.get_topic_info(), json.dumps(self.info), retain = False, qos = 1)

    def authenticate(self):
        self.log("Authenticating device...")
        mqtt.connected_flag = False
        self.state = self.AUTHENTICATING
        self.client = mqtt(client_id = self.token, server = self.host,
                            port = self.port, user = self.token, password = self.token,
                            keepalive = self.keepalive)
        self.set_will()
        self.client.set_callback(self.on_message)
        if not self.client.connect(clean_session = True):
            self.log("Connect OK!")
        else:
            self.log("Connect FAIL!")
            raise ERaError("Authenticating timeout")

        self.subscribe(self.topic_down.format(self.token), qos = 1)
        self.subscribe(self.topic_virtual_pin.format(self.token), qos = 1)
        self.publish_state()
        self.state = self.AUTHENTICATED
        self.log("Access granted")

    def is_server_alive(self):
        now = ticks_ms()
        keepalive_ms = self.keepalive * const(1000)
        ping_delta = time.ticks_diff(now, self.last_ping_time)
        if ping_delta > keepalive_ms:
            return False
        if ping_delta > keepalive_ms // const(2):
            self.client.ping()
            self.log("Ping time: {}".format(now))
            self.last_ping_time = now
        return True

    def loop(self):
        ret = self.client.check_msg()
        if ret != None and ret < 0:
            self._disconnect()
        if not self.is_server_alive():
            self.disconnect("Server is offline")

    def connected(self):
        return True if self.state == self.AUTHENTICATED else False

class ERa(Connection, Timer):
    events = {}

    def __init__(self, token, **kwargs):
        Connection.__init__(self, token, **kwargs)
        Timer.__init__(self, False)
        self.last_ping_time = ticks_ms()
        self.state = self.DISCONNECTED
        print(LOGO.format(__version__, "MicroPython"))

    def on_message(self, topic, msg):
        self.log("Message {} ({}): {}".format(topic.decode("utf-8"), len(msg), msg.decode("utf-8")))
        try:
            msg_type, msg_id, msg_data = self.parse_response(topic.decode("utf-8"), msg.decode("utf-8"))
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

    def disconnect(self, err_msg = None):
        self._disconnect()
        self.call_handler(self.DISCONNECT_EVENT)
        if err_msg:
            self.log("Disconnected: {}".format(err_msg))
        time.sleep(self.RECONNECT_SLEEP)

    def virtual_write(self, v_pin, value, **kwargs):
        data = self.virtual_write_msg(v_pin, ("v", value), **kwargs)
        if data:
            self.publish(data["topic"], json.dumps(data["payload"]), retain = True, qos = 1)

    def register_timer(era, *args, **kwargs):
        return Timer.register(era, *args, **kwargs)

    def register_handler(era, event_name):
        class Deco(object):
            def __init__(self, func):
                self.func = func
                if str(event_name).lower() in (era.VPIN_READ_ALL, era.VPIN_WRITE_ALL):
                    event_base_name = str(event_name).split(era.VPIN_WILDCARD)[0]
                    for i in range(era.VPIN_MAX_NUM + const(1)):
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
            else:
                self.loop()
        except KeyboardInterrupt:
            raise
        except OSError as o_err:
            self.log(o_err)
        except ERaError as e_err:
            self.disconnect(e_err)
        except Exception as g_exc:
            self.disconnect(g_exc)
