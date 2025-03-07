import paho.mqtt.client as mqtt
import ssl
import time
import json 
from dotenv import load_dotenv
import os
from detect import request_image_and_detect
from sql import save_bin_level,save_bin_status,get_bin_status,handle_report_status,get_bin_location
from Telegram import sendmessageto

load_dotenv()

mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = 8883
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
mqtt_camera = "junker/+/camera"
mqtt_binlevel = "junker/+/binLevel"
mqtt_status = "junker/+/online"

bin_status_times = {}
bin_last_status = {}  
BIN_TIMEOUT = 40


def monitor_bin_status():
    while True:
        current_time = time.time()
        offline_bins = []  # เก็บ bin ที่ต้องลบออกจาก bin_status_times

        for bin_id, last_time in list(bin_status_times.items()):
            if current_time - last_time > BIN_TIMEOUT:
                location = get_bin_location(bin_id)
                print(f"⚠️ Bin {bin_id} is offline (timeout).")

                save_bin_status(bin_id, 0)
                handle_report_status(bin_id, status=0)

                # ส่งแจ้งเตือนเฉพาะครั้งแรกที่ offline เท่านั้น
                if bin_last_status.get(bin_id, 1) == 1:
                    sendmessageto("admin", f"⚠️ เกิดข้อผิดพลาดกับถังขยะหมายเลขที่ {bin_id} - {location}")

                bin_last_status[bin_id] = 0  # อัปเดตสถานะเป็น offline
                offline_bins.append(bin_id)

        # ลบออกจาก bin_status_times หลังจากวนลูปเสร็จ
        for bin_id in offline_bins:
            del bin_status_times[bin_id]

        time.sleep(5)



# ฟังก์ชัน Callback เมื่อได้รับข้อความ
def on_message(client, userdata, message):
    payload = message.payload.decode()  # ดึงข้อความจาก MQTT
    topic = message.topic
    machine_id = topic.split('/')[1]  # แยก Machine ID จาก topic

    if len(payload.split(" ")) > 1 and payload.split(" ")[0] == "send_img":
        url = payload.split(" ")[1]  # ดึง URL ที่ส่งมา
        status = get_bin_status(machine_id)
        if status == 0:
            print("ถังขยะอาจเกิดข้อผิดพลาด ไม่สามารถส่งข้อมูลได้")
        else:
            request_image_and_detect(machine_id, url)  # เรียกฟังก์ชันขอภาพ
            
    elif "online" in topic:
        location = get_bin_location(machine_id)
        print(f"✅ Bin {machine_id} is online.")

        # เช็คว่าก่อนหน้านี้สถานะเป็น offline หรือไม่
        if bin_last_status.get(machine_id, 1) == 0:
            sendmessageto("admin", f"✅ ถังขยะที่ {machine_id} - {location} กลับมาออนไลน์แล้ว")
        
        if bin_last_status.get(machine_id, 1) == 1:
            return

        # อัปเดตสถานะเป็น online
        handle_report_status(machine_id, status=1)
        save_bin_status(machine_id, 1)
        bin_status_times[machine_id] = time.time()
        bin_last_status[machine_id] = 1  # อัปเดตสถานะเป็น online

    
    elif "binLevel" in topic:
        try:
            bin_data = json.loads(payload)  # แปลงข้อความ JSON เป็น Dictionary
            bin_level_bottle = bin_data.get("bin_level_bottle", 0)
            bin_level_can = bin_data.get("bin_level_can", 0)
            bin_level_papercup = bin_data.get("bin_level_papercup", 0)
            bin_level_others = bin_data.get("bin_level_others", 0)

            print(f"Updated bin levels: bottle={bin_level_bottle}, can={bin_level_can}, papercup={bin_level_papercup}, others={bin_level_others}")
            save_bin_level(
                bin_id=machine_id,
                bin_level_bottle=bin_level_bottle,
                bin_level_can=bin_level_can,
                bin_level_papercup=bin_level_papercup,
                bin_level_others=bin_level_others
            )

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
    
    else:
        print(f"Unhandled message on topic {topic}: {payload}")


# ฟังก์ชัน Callback เมื่อเชื่อมต่อกับ MQTT Broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully.")
        client.subscribe(mqtt_camera)
        client.subscribe(mqtt_binlevel)
        client.subscribe(mqtt_status)
        print(f"Subscribed to topic {mqtt_camera}")
        print(f"Subscribed to topic {mqtt_binlevel}")
        print(f"Subscribed to topic {mqtt_status}")
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")

# ฟังก์ชัน Callback เมื่อหลุดการเชื่อมต่อ
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected from MQTT broker unexpectedly. Attempting to reconnect...")
    else:
        print("Disconnected from MQTT broker.")

    while True:
        try:
            client.reconnect()
            print("Reconnected to MQTT broker successfully.")
            break
        except Exception as e:
            print(f"Reconnect failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# สร้าง MQTT Client และตั้งค่าฟังก์ชัน Callback
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# เชื่อมต่อกับ MQTT Broker และกำหนดค่า keepalive เป็น 60 วินาที
client.connect(mqtt_broker, mqtt_port, keepalive=60)
