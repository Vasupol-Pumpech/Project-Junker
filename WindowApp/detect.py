import requests
import numpy as np
import cv2
from ultralytics import YOLO
import mqtt_config
from datetime import datetime
import threading
import os
import sys
from sql import save_garbage_data, get_bin_level, get_bin_Alert, get_bin_location
from Telegram import sendmessageto
from GarbageDetails import GarbageDetailsWindow
from PyQt5.QtCore import QCoreApplication

# หา path ที่ .exe หรือ .py รันอยู่
if getattr(sys, 'frozen', False):  # ถ้ารันจาก .exe
    script_dir = os.path.dirname(sys.executable)
else:  # ถ้ารันจาก .py
    script_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(script_dir, "junker.pt")  # ไฟล์ต้องอยู่ที่เดียวกับ .exe

if os.path.exists(model_path):
    model = YOLO(model_path)
    print(f"✅ Model loaded from: {model_path}")
else:
    print(f"❌ Warning: {model_path} not found! Please put the model in the same folder as the exe.")

# ฟังก์ชันสำหรับเซฟภาพหลังการตรวจจับ
def save_detected_image(img, best_class):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # สร้าง timestamp สำหรับชื่อไฟล์
    file_name = f"img_detect/{best_class}_{timestamp}.jpg"  # ตั้งชื่อไฟล์ให้สัมพันธ์กับประเภทของวัตถุและเวลา
    
    # สร้างโฟลเดอร์ถ้ายังไม่มี
    if not os.path.exists("img_detect"):
        os.makedirs("img_detect")

    detected_img = img.plot()  # แสดงผลภาพหลังการตรวจจับ (มีกรอบการตรวจจับ)
    cv2.imwrite(file_name, detected_img)  # บันทึกภาพลงในโฟลเดอร์ img_detect
    print(f"Saved detected image as {file_name}")  # พิมพ์ชื่อไฟล์ที่บันทึก

    return file_name  # คืนพาธของไฟล์

# ฟังก์ชันในการขอภาพและตรวจจับวัตถุ
def request_image_and_detect(machine_id, url):
    print(f"Requesting image from ESP32 (Machine ID: {machine_id}) at {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            nparr = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                
                print("✅ Image successfully decoded. Running YOLO model...")
                print(f"🔍 Model Path: {model_path}")  # เช็คว่ารันโมเดลจากที่ไหน
                print(f"🔍 Model Object: {model}")  # เช็คว่าโมเดลถูกโหลดหรือไม่

                results = model(img)
                print(f"🔍 YOLO Detection Results: {results}")
                
                # ตรวจสอบว่ามีวัตถุหรือไม่
                if results and len(results[0].boxes) > 0:
                    best_box = results[0].boxes[0]
                    print(f"🔍 Best Box: {best_box}")  # Debugging
                    print(f"🔍 All Names in YOLO: {results[0].names}")  # Debugging
                    
                    best_class = results[0].names.get(int(best_box.cls), "unknown")

                    print(f"✅ Detected Class: {best_class}")  # Debugging
                    new_class = ""

                    # ดึงข้อมูลปัจจุบันจากฐานข้อมูล
                    if best_class == "bottle":
                        current_amount = get_bin_level(machine_id, column="bottle_amount")
                        new_class ="ขวด"
                    elif best_class == "can":
                        current_amount = get_bin_level(machine_id, column="can_amount")
                        new_class ="กระป๋อง"
                    elif best_class == "papercup":
                        current_amount = get_bin_level(machine_id, column="papercup_amount")
                        new_class ="แก้วกระดาษ"
                    else:  # non_object
                        current_amount = get_bin_level(machine_id, column="others_amount")
                        
                    detected_topic = f"junker/{machine_id}/detected"
                    mqtt_config.client.publish(detected_topic, best_class, qos=1)
                    print(f"Published '{best_class}' to topic {detected_topic}")  

                    location = get_bin_location(machine_id)
                    bin_data = get_bin_Alert(machine_id)

                    if bin_data:
                        bin_level = bin_data.get('bin_level')
                        bin_notify = bin_data.get('bin_notify')  
                    
                    if current_amount and current_amount.get(f"{best_class}_amount", 0) >= bin_notify and current_amount and current_amount.get(f"{best_class}_amount", 0) < bin_level :
                        sendmessageto("user",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}                            
🚨 ช่อง {new_class} ใกล้เต็มแล้ว""")
                        sendmessageto("admin",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}                            
🚨 ช่อง {new_class} ใกล้เต็มแล้ว""")
                    elif current_amount and current_amount.get(f"{best_class}_amount", 0) >= bin_level:
                        print(f"Skipping save for {best_class} as it exceeds max_level ({bin_level})")
                        sendmessageto("user",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง {new_class} เต็มแล้ว""")
                        sendmessageto("admin",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง {new_class} เต็มแล้ว""")
                        # return

                    # เซฟภาพและได้รับพาธของไฟล์
                    file_path = save_detected_image(results[0], best_class)

                    # บันทึกข้อมูลลงในฐานข้อมูล
                    save_garbage_data(machine_id, best_class, file_path)
                    print("✅ ข้อมูลขยะถูกบันทึกแล้ว กำลังอัปเดต UI")

                    app = QCoreApplication.instance()
                    if app:
                        for widget in app.topLevelWidgets():
                            if isinstance(widget, GarbageDetailsWindow):
                                widget.garbage_updated.emit()  # ใช้ signal เพื่ออัปเดต UI
                                print("✅ อัปเดต UI เรียบร้อยแล้ว")


                else:
                    # หากไม่พบวัตถุ ส่งข้อความ 'non_object'
                    detected_topic = f"junker/{machine_id}/detected"
                    mqtt_config.client.publish(detected_topic, "non_object", qos=1)
                    print(f"Published 'non_object' to topic {detected_topic}")

                    # ดึงข้อมูลปัจจุบันสำหรับ non_object
                    current_amount = get_bin_level(machine_id, column="others_amount")

                    location = get_bin_location(machine_id)
                    bin_data = get_bin_Alert(machine_id)
                    if bin_data:
                        bin_level = bin_data.get('bin_level')
                        bin_notify = bin_data.get('bin_notify')  

                    if current_amount and current_amount.get("others_amount", 0) >= bin_notify and current_amount and current_amount.get("others_amount", 0) < bin_level :
                        sendmessageto("user",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง อื่นๆ ใกล้เต็มแล้ว""")   
                        sendmessageto("admin",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง อื่นๆ ใกล้เต็มแล้ว""")   
                    elif current_amount and current_amount.get("others_amount", 0) >= bin_level:
                        print(f"Skipping save for non_object as it exceeds max_level ({bin_level})")
                        sendmessageto("user",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง อื่นๆ เต็มแล้ว""")
                        sendmessageto("admin",f"""📌 ถังที่ {machine_id} ตำแหน่ง {location}
🚨 ช่อง อื่นๆ เต็มแล้ว""")
                        # return
                    

                    # เซฟภาพกรณีที่ไม่พบวัตถุ
                    file_path = save_detected_image(results[0], "non_object")

                    # บันทึกข้อมูลลงในฐานข้อมูล
                    save_garbage_data(machine_id, "non_object", file_path)
                    print("✅ ข้อมูลขยะถูกบันทึกแล้ว กำลังอัปเดต UI")
    
                    app = QCoreApplication.instance()
                    if app:
                        for widget in app.topLevelWidgets():
                            if isinstance(widget, GarbageDetailsWindow):
                                widget.garbage_updated.emit()  # ใช้ signal เพื่ออัปเดต UI
                                print("✅ อัปเดต UI เรียบร้อยแล้ว")
                    

            else:
                print("Failed to decode the image")
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while requesting image: {e}")
