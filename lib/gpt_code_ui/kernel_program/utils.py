import re
import json
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message

import gpt_code_ui.kernel_program.config as config

def escape_ansi(line):
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def send_json(messaging, message, identity):
    message = snakemq.message.Message(json.dumps(message).encode("utf-8"), ttl=600)
    messaging.send_message(identity, message)

def init_snakemq(ident, init_type="listen"):
    link = snakemq.link.Link()
    packeter = snakemq.packeter.Packeter(link)
    messaging = snakemq.messaging.Messaging(ident, "", packeter)
    if init_type == "listen":
        link.add_listener(("localhost", config.SNAKEMQ_PORT))
    elif init_type == "connect":
        link.add_connector(("localhost", config.SNAKEMQ_PORT))
    else:
        raise Exception("Unsupported init type.")
    return messaging, link