try:
    from .era import ERa
except ImportError:
    from .era_wifi import WiFi
    from .era_micro import ERa
