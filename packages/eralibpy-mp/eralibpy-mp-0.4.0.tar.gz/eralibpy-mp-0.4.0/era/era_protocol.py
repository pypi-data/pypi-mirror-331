try:
    import json

    def const(value):
        return value
except ImportError:
    import ujson as json
    from micropython import const

from era.era_const import Const

class Protocol(Const):
    def __init__(self, token):
        self.config = []
        self.token = token

    def pack_msg(self, *args, **kwargs):
        data = kwargs
        for key, value in args:
            data[key] = value
        return data

    def parse_response(self, topic, payload):
        topic_args = []
        topic_args = [itm for itm in topic.split("/")]
        try:
            if len(topic_args) >= const(5):
                return topic_args[3], topic_args[4], json.loads(payload)
            else:
                return topic_args[3], None, json.loads(payload)
        except ValueError:
            return None

    def config_write_msg(self, v_pin, *args, **kwargs):
        data = {
            "topic" : self.topic_config.format(self.token, v_pin),
            "payload" : self.pack_msg(*args, **kwargs)
        }
        return data

    def lwt_write_msg(self):
        data = {
            "topic" : self.topic_state.format(self.token),
            "payload" : {
                "ol" : 0
            }
        }
        return data

    def state_write_msg(self):
        data = {
            "topic" : self.topic_state.format(self.token),
            "payload" : {
                "ol" : 1,
                "ask_configuration" : 1
            }
        }
        return data

    def get_topic_info(self):
        return self.topic_info.format(self.token)

    def virtual_write_msg(self, v_pin, *args, **kwargs):
        try:
            config_id = next((info["config_id"] for info in self.config if info["pin_number"] == v_pin))
            return self.config_write_msg(config_id, *args, **kwargs) if config_id else None
        except StopIteration:
            pass
        return None
