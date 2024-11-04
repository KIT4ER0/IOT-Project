# โค้ดนี้ใช้สำหรับอ่านค่าจาก SHT31 และส่งผ่าน MQTT

import smbus
import time
import paho.mqtt.client as mqtt

# กำหนดที่อยู่ของ SHT31 บน I2C
SHT31_I2C_ADDRESS = 0x44

# ตั้งค่า MQTT
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_TOPIC = "project/IOT"

# ตั้งค่า I2C bus
bus = smbus.SMBus(1)

# สร้าง client สำหรับ MQTT
mqttc = mqtt.Client()
mqttc.connect(MQTT_BROKER, MQTT_PORT)

def read_sht31():
    # ส่งคำสั่งไปยัง SHT31 เพื่อเริ่มการวัด
    bus.write_i2c_block_data(SHT31_I2C_ADDRESS, 0x2C, [0x06])
    time.sleep(0.5)

    # อ่านข้อมูล 6 ไบต์จากเซ็นเซอร์
    data = bus.read_i2c_block_data(SHT31_I2C_ADDRESS, 0x00, 6)

    # แปลงข้อมูลที่อ่านได้
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    return cTemp, humidity

# เริ่มการวัดและส่งข้อมูลผ่าน MQTT
while True:
    # อ่านค่าอุณหภูมิและความชื้น
    temperature, humidity = read_sht31()

    # สร้างข้อความที่จะส่ง
    message = f"Temperature: {temperature:.2f} °C, Humidity: {humidity:.2f} %RH"

    # ส่งข้อมูลไปยัง MQTT
    mqttc.publish(MQTT_TOPIC, message)
    print(f"Sent: {message}")

    # เวลารอระหว่างการส่งข้อมูล
    time.sleep(2)
