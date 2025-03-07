import time
import mqtt_config
from datetime import datetime
import threading
import schedule
from PyQt5.QtWidgets import QApplication
from GarbageDetails import GarbageDetailsWindow
from Telegram import telegram_loop, send_garbage_summary

# ตัวแปรเก็บสถานะการแจ้งเตือน
last_notified_day = None
last_notified_month = None
last_notified_year = None

# ฟังก์ชันหลักสำหรับ MQTT loop และ image detection
def mqtt_and_detect_loop():
    try:
        while True:
            mqtt_config.client.loop()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program stopped.")

def schedule_notifications():
    global last_notified_day, last_notified_month, last_notified_year

    # ตั้งเวลาส่งรายวัน
    schedule.every().day.at("20:00").do(send_garbage_summary, "day")

    while True:
        try:
            now = datetime.now()

            # ส่งแจ้งเตือนรายเดือนเฉพาะวันแรกของเดือน และยังไม่เคยส่งในเดือนนั้น
            if now.day == 1 and last_notified_month != now.month:
                send_garbage_summary("month")
                last_notified_month = now.month  # อัปเดตสถานะว่าเดือนนี้แจ้งเตือนแล้ว

            # ส่งแจ้งเตือนรายปีเฉพาะวันที่ 1 มกราคม และยังไม่เคยส่งในปีนั้น
            if now.month == 1 and now.day == 1 and last_notified_year != now.year:
                send_garbage_summary("year")
                last_notified_year = now.year  # อัปเดตสถานะว่าแจ้งเตือนรายปีแล้ว

            schedule.run_pending()
        except Exception as e:
            print(f"Error in schedule_notifications: {e}")
        time.sleep(60)  # ตรวจสอบทุก 60 วินาที
        
if __name__ == "__main__":

    # เริ่มฟังก์ชันตรวจสอบ bin_status
    bin_status_thread = threading.Thread(target=mqtt_config.monitor_bin_status, daemon=True)
    bin_status_thread.start()

    # เริ่ม MQTT และ image detection
    mqtt_thread = threading.Thread(target=mqtt_and_detect_loop, daemon=True)
    mqtt_thread.start()

    # เริ่ม Telegram
    telegram_thread = threading.Thread(target=telegram_loop, daemon=True)
    telegram_thread.start()

    # เริ่ม Thread สำหรับแจ้งเตือนอัตโนมัติ
    notification_thread = threading.Thread(target=schedule_notifications, daemon=True)
    notification_thread.start()
        
    # เริ่ม PyQt5 GUI
    app = QApplication([])
    window = GarbageDetailsWindow()
    window.show()
    app.exec_()
