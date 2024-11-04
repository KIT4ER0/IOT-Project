import asyncio
import websockets
import paho.mqtt.client as mqtt
import time
from LCD import LCD
import RPi.GPIO as GPIO

# MQTT Configuration
MQTT_BROKER = 'mqtt-dashboard.com'
MQTT_PORT = 1883
MQTT_TOPIC = 'project/IOT'

# LED GPIO Pin
LED_PIN = 18  # GPIO18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# LCD Setup
lcd = LCD(2, 0x27, True)
lcd.clear()

# Global variable to store the latest sensor data
sensor_data = {"temperature": None, "humidity": None}

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, message):
    global sensor_data
    data = message.payload.decode()
    print(f"Received message '{data}' on topic '{message.topic}'")

    try:
        # Parse temperature and humidity from the received MQTT message
        temp_str = data.split(",")[0].split(":")[1].strip().replace("°C", "")
        humidity_str = data.split(",")[1].split(":")[1].strip().replace("%RH", "")
        temperature = float(temp_str)
        humidity = float(humidity_str)

        # Update global sensor data
        sensor_data["temperature"] = temperature
        sensor_data["humidity"] = humidity

        # Display on LCD
        lcd.clear()
        lcd.message(f"Temp: {temperature:.1f}C", 1)
        lcd.message(f"Humidity: {humidity:.1f}%", 2)

        # Control LED
        if temperature > 30:
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)

    except ValueError:
        print("Error parsing temperature or humidity data.")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# WebSocket server handler
async def websocket_handler(websocket, path):
    while True:
        if sensor_data["temperature"] is not None and sensor_data["humidity"] is not None:
            data_to_send = f"Temperature: {sensor_data['temperature']} °C, Humidity: {sensor_data['humidity']} %RH"
            await websocket.send(data_to_send)
        await asyncio.sleep(1)

# Start WebSocket server
start_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)

# Main event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    lcd.clear()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
