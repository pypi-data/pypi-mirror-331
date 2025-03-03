try:
    from micropython import const
except ImportError:
    def const(value):
        return value

LOGO = const("""
      ____  ____              
     / _   / _  \\  _          
    /____ / / __/ /.\\         
     / _ /  _ \\  / _ \\      
    /___/__//_/`/_/ \\_\\     
               (v{} for {})\r\n""")

class Const(object):
    VPIN_MAX_NUM = const(64)

    RECONNECT_SLEEP = const(1)
    TASK_PERIOD_RES = const(50)
    DISCONNECTED = const(0)
    CONNECTING = const(1)
    AUTHENTICATING = const(2)
    AUTHENTICATED = const(3)

    VPIN_WILDCARD = const("*")
    VPIN_READ = const("read v")
    VPIN_WRITE = const("write v")
    CONNECT_EVENT = const("connect")
    DISCONNECT_EVENT = const("disconnect")
    VPIN_READ_ALL = const("{}{}").format(VPIN_READ, VPIN_WILDCARD)
    VPIN_WRITE_ALL = const("{}{}").format(VPIN_WRITE, VPIN_WILDCARD)

    topic_down = const("eoh/chip/{}/down")
    topic_virtual_pin = const("eoh/chip/{}/virtual_pin/+")

    topic_info = const("eoh/chip/{}/info")
    topic_state = const("eoh/chip/{}/is_online")
    topic_config = const("eoh/chip/{}/config/{}/value")
    topic_config_multi = const("eoh/chip/{}/config_value")
