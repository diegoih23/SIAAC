"""Escucha comandos MQTT del backend y controla GPIO locales (opcional).

Útil si la sirena o las luces están conectadas directamente a la Raspberry Pi
en lugar del ESP32. En el prototipo base los actuadores cuelgan del ESP32.
"""
import json
import logging
import time

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT, MQTT_TOPIC_COMMANDS

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("mqtt")


def handle_command(command: dict) -> None:
    logger.info("Comando recibido: %s", command)
    # Ejemplo con gpiozero (instalar con: pip install gpiozero):
    # from gpiozero import Buzzer, LED
    # buzzer = Buzzer(26)
    # light = LED(25)
    # (buzzer if action in ("SIREN", "BOTH") else ...).on()
    # time.sleep(duration)
    # ...off()
    time.sleep(float(command.get("duration_seconds", 10)))
    logger.info("Comando finalizado")


def on_connect(client, userdata, flags, reason_code, properties=None):
    logger.info("Conectado al broker MQTT (%s)", reason_code)
    client.subscribe(MQTT_TOPIC_COMMANDS)


def on_message(client, userdata, message):
    try:
        handle_command(json.loads(message.payload.decode("utf-8")))
    except json.JSONDecodeError:
        logger.warning("Payload inválido en %s", message.topic)


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="siaac-raspberry")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
