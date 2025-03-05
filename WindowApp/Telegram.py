import requests
from sql import (get_bin_level_location, get_user_role_sql, get_user_info_sql, save_user_sql, get_all_users,
                delete_user_by_name, get_all_user_names,get_bin_ids_with_location,get_garbage_summary)
from datetime import datetime, timedelta

API_Token = "7865144579:AAFsnmxR_YViwwpwh_f3FPB6U9PIiTMYRhg"
ADMIN_PASSWORD = "2523"  

def get_updates(offset=None):
    apiURL = f'https://api.telegram.org/bot{API_Token}/getUpdates'
    params = {'offset': offset} if offset else {}
    try:
        response = requests.get(apiURL, params=params)
        updates = response.json()
        if updates["ok"]:
            return updates["result"]
    except Exception as e:
        print(f"Error fetching updates: {e}")
    return []

def sendmessage(chat_id, message):
    apiURL = f'https://api.telegram.org/bot{API_Token}/sendMessage'
    try:
        requests.post(apiURL, json={'chat_id': chat_id, 'text': message})
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")

def save_user(chat_id, name=None, role="user"):
    save_user_sql(chat_id, name, role)

def get_user_info(chat_id):
    return get_user_info_sql(chat_id) or {}

def get_user_role(chat_id):
    return get_user_role_sql(chat_id)

def sendmessageto(role, message):
    users = get_all_users()  # ดึงข้อมูลผู้ใช้ทั้งหมด
    for user in users:
        if user["role"] == role:
            sendmessage(user["chat_id"], message)  # ส่งข้อความไปยังผู้ใช้ที่มี role ตรงกัน

def list_all_users_command(chat_id):
    """ให้ admin ดูรายชื่อผู้ใช้ทั้งหมด"""
    if get_user_role(chat_id) != "admin":
        sendmessage(chat_id, "❌ คุณไม่มีสิทธิ์ดูรายชื่อผู้ใช้!")
        return

    users = get_all_user_names()
    if not users:
        sendmessage(chat_id, "🔍 ไม่พบรายชื่อผู้ใช้ในระบบ!")
        return

    message = "📋 รายชื่อผู้ใช้ทั้งหมด:\n"
    for user in users:
        message += f"- {user['name']} ({user['role']})\n"

    sendmessage(chat_id, message)

def delete_user_by_name_command(chat_id, target_name):
    """ให้ admin ลบ user ตามชื่อ"""
    if get_user_role(chat_id) != "admin":
        sendmessage(chat_id, "❌ คุณไม่มีสิทธิ์ในการลบผู้ใช้!")
        return

    if delete_user_by_name(target_name):
        sendmessage(chat_id, f"✅ ลบผู้ใช้ '{target_name}' สำเร็จ!")
    else:
        sendmessage(chat_id, f"❌ ไม่พบผู้ใช้ '{target_name}' หรือเกิดข้อผิดพลาดในการลบ!")

def list_all_bins(chat_id):

    """ให้ผู้ใช้ดูรายการเครื่องทั้งหมดพร้อมสถานที่"""
    bins = get_bin_ids_with_location()
    
    if not bins:
        sendmessage(chat_id, "🔍 ไม่พบเครื่องขยะในระบบ!")
        return

    message = "📋 รายการถังขยะทั้งหมด:\n"
    for bin_data in bins:
        message += f"- หมายเลข {bin_data['bin_id']} (สถานที่: {bin_data['bin_location']})\n"

    sendmessage(chat_id, message)


# ชื่อเดือนภาษาไทย
thai_months = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def send_garbage_summary(date_type="day"):
    """ ส่งข้อมูลปริมาณขยะผ่าน Telegram พร้อมระบุวัน/เดือน/ปี ของไทย """

    now = datetime.now()
    
    # คำนวณวันที่ที่ใช้ในรายงาน
    if date_type == "day":
        report_date = f"{now.day} {thai_months[now.month - 1]} {now.year + 543}"  # วันนี้ (วัน เดือน พ.ศ.)
    elif date_type == "month":
        last_month = now.month - 1 if now.month > 1 else 12  # เดือนที่แล้ว
        last_year = now.year if now.month > 1 else now.year - 1  # ปรับปีถ้าเดือนเป็น ม.ค.
        report_date = f"{thai_months[last_month - 1]} {last_year + 543}"
    elif date_type == "year":
        report_date = f"{now.year + 543 - 1}"  # ปีที่แล้ว (พ.ศ.)
    else:
        report_date = "ไม่ระบุ"

    # ดึงข้อมูลสรุปขยะ
    summary = get_garbage_summary(date_type)
    
    if not summary:
        message = f"📢 ไม่พบข้อมูลปริมาณขยะสำหรับ {date_type} ({report_date})"
    else:
        message = f"📢 รายงานปริมาณขยะ ({report_date}) 📢\n"
        total_count = sum(item["count"] for item in summary)
        message += f"🗑️ ขยะทั้งหมด: {total_count} ชิ้น\n"

        icon_map = {
            "bottle": "🍾 ขวด",
            "can": "🥫 กระป๋อง",
            "papercup": "🥤 แก้วกระดาษ",
            "non_object": "🗑️ อื่นๆ"
        }

        for item in summary:
            garbage_type = icon_map.get(item["garbage_type"], item["garbage_type"])
            message += f"- {garbage_type}: {item['count']} ชิ้น\n"

    # ส่งข้อความไปยัง Telegram
    sendmessageto("admin", message)

def test_garbage_notifications():
    """ ทดสอบแจ้งเตือนรายวัน รายเดือน รายปี """
    send_garbage_summary("day")
    send_garbage_summary("month")
    send_garbage_summary("year")

def process_user_message(chat_id, message_text):
    user_info = get_user_info(chat_id)
    
    if not user_info.get("name"):
        if message_text.lower().startswith("ตั้งชื่อ "):
            name = message_text[9:]
            save_user(chat_id, name=name)
            sendmessage(chat_id, f"ชื่อของคุณถูกตั้งเป็น '{name}' เรียบร้อยแล้ว!")
        else:
            sendmessage(chat_id, "กรุณาตั้งชื่อของคุณ โดยพิมพ์: ตั้งชื่อ (ชื่อ)")
        return
    
    if message_text.startswith("ปริมาณขยะ"):
        try:
            bin_id = int(message_text.replace("ปริมาณขยะ", "").strip())
            bin_data = get_bin_level_location(bin_id)
        
            if bin_data:
                location = bin_data.get('bin_location', '📍 ไม่ทราบสถานที่')
                message = f"""🗑️ **ข้อมูลปริมาณขยะ**
📍 สถานที่: {location}
🔢 หมายเลขถัง: {bin_id}

♻️ ปริมาณขยะในถัง
- 🍾 ขวด: {bin_data.get('bottle', 0)}%
- 🥫 กระป๋อง: {bin_data.get('can', 0)}%
- 🥤 แก้วกระดาษ: {bin_data.get('paper_cup', 0)}%
- 🗑️ อื่นๆ: {bin_data.get('other', 0)}%"""
                sendmessage(chat_id, message)
            else:
                sendmessage(chat_id, f"❌ ไม่พบข้อมูลสำหรับถังขยะหมายเลข {bin_id}")
        except ValueError:
            sendmessage(chat_id, "⚠️ รูปแบบคำขอไม่ถูกต้อง กรุณาพิมพ์ในรูปแบบ **'ปริมาณขยะ (หมายเลข)'**")

    
    elif message_text.lower().startswith("ฉันต้องการเป็น admin"):
        if get_user_role(chat_id) == "admin":
            sendmessage(chat_id, "คุณเป็น Admin อยู่แล้ว!")
        elif message_text.endswith(ADMIN_PASSWORD):
            user_info = get_user_info(chat_id)
            save_user(chat_id, name=user_info.get("name", "ผู้ใช้"), role="admin")
            if get_user_role(chat_id) == "admin":
                sendmessage(chat_id, "คุณได้รับการเลื่อนเป็น Admin แล้ว!")
            else:
                sendmessage(chat_id, "เกิดข้อผิดพลาดในการเปลี่ยนเป็น Admin กรุณาลองอีกครั้ง!")
        else:
            sendmessage(chat_id, "รหัสผ่านไม่ถูกต้อง กรุณาลองอีกครั้ง!")
    
    elif message_text.lower().startswith("ฉันต้องการเป็น user"):
        if get_user_role(chat_id) == "user":
            sendmessage(chat_id, "คุณเป็น User อยู่แล้ว!")
        else:
            user_info = get_user_info(chat_id)
            save_user(chat_id, name=user_info.get("name", "ผู้ใช้"), role="user")
            if get_user_role(chat_id) == "user":
                sendmessage(chat_id, "คุณถูกลดระดับเป็น User แล้ว!")
            else:
                sendmessage(chat_id, "เกิดข้อผิดพลาดในการเปลี่ยนเป็น User กรุณาลองอีกครั้ง!")

    elif message_text.lower() == "ดูรายชื่อทั้งหมด":
        list_all_users_command(chat_id)

    elif message_text.lower().startswith("ลบผู้ใช้ "):
        target_name = message_text[9:].strip()
        delete_user_by_name_command(chat_id, target_name)
        
    elif message_text.lower() == "ดูรายการเครื่อง":
        list_all_bins(chat_id)

    elif message_text.lower() == "เทสแจ้งเตือน":
        if get_user_role(chat_id) != "admin":
            sendmessage(chat_id, "คุณไม่มีสิทธิ์ใช้คำสั่งนี้! เฉพาะ Admin เท่านั้น")
            return
        
        sendmessage(chat_id, "กำลังทดสอบการแจ้งเตือน โปรดรอสักครู่...")
        test_garbage_notifications()
        sendmessage(chat_id, "การทดสอบแจ้งเตือนเสร็จสิ้น!")

    else:
        role = get_user_role(chat_id)
        if role == "admin":
            sendmessage(chat_id, """✨ ตัวเลือกใช้งาน Admin ✨
1. ดูรายการเครื่อง
2. ปริมาณขยะ (หมายเลขของถัง)
3. ฉันต้องการเป็น admin 2523
4. ฉันต้องการเป็น user
5. ดูรายชื่อทั้งหมด
6. ลบผู้ใช้ (ชื่อ)
7. เทสแจ้งเตือน""")

        else:
            sendmessage(chat_id, """✨ ตัวเลือกใช้งาน ✨
1. ดูรายการเครื่อง
2. ปริมาณขยะ (หมายเลข)""")


def telegram_loop():
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                message_text = update["message"].get("text", "").strip()
                process_user_message(chat_id, message_text)
            offset = update["update_id"] + 1
