from datetime import datetime
import pymysql
import pymysql.cursors


def get_database_connection():
        """
        ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล

        """
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',  
                database='junker',
                charset='utf8mb4'
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")
            return None

# ฟังก์ชันบันทึกข้อมูลขยะลงใน tbl_garbage
def save_garbage_data(machine_id, garbage_type, garbage_img_path):
    """
    บันทึกข้อมูลขยะลงใน tbl_garbage โดยใช้ machine_id เป็น bin_id
    """
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return False  # คืนค่า False ถ้าเชื่อมต่อฐานข้อมูลไม่สำเร็จ

    cursor = db.cursor()

    try:
        # คำสั่ง SQL สำหรับการบันทึกข้อมูล
        cursor.execute("""
            INSERT INTO tbl_garbage (bin_id, garbage_type, garbage_date, garbage_img)
            VALUES (%s, %s, %s, %s)
        """, (machine_id, garbage_type, datetime.now(), garbage_img_path))

        db.commit()
        print(f"Data for garbage type '{garbage_type}' saved successfully.")
        return True  # คืนค่า True ถ้าบันทึกสำเร็จ

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return False  # คืนค่า False ถ้ามี error
    
    finally:
        cursor.close()
        db.close()

        
def delete_garbage(garbage_id):
    """ลบขยะตาม garbage_id"""
    db = get_database_connection()
    if not db:
        return False

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM tbl_garbage WHERE garbage_id = %s", (garbage_id,))
        db.commit()
        return True
    except pymysql.MySQLError as e:
        print(f"Error deleting garbage: {e}")
        return False
    finally:
        cursor.close()
        db.close()


def delete_all_garbage(bin_id):
    """ลบข้อมูลขยะทั้งหมดของถังขยะที่เลือก"""
    db = get_database_connection()
    if not db:
        return False

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM tbl_garbage WHERE bin_id = %s", (bin_id,))
        db.commit()
        return True
    except pymysql.MySQLError as e:
        print(f"Error deleting all garbage for bin_id {bin_id}: {e}")
        return False
    finally:
        cursor.close()
        db.close()


# ฟังก์ชันบันทึกข้อมูลจำนวนขยะในถัง
def save_bin_level(bin_id, bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others):
    """บันทึกหรืออัปเดตข้อมูล bin level ลงใน tbl_bin_detail"""
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return

    cursor = db.cursor()

    try:
        # ตรวจสอบว่ามี bin_id อยู่แล้วหรือไม่
        cursor.execute("SELECT COUNT(*) FROM tbl_bin_detail WHERE bin_id = %s", (bin_id,))
        result = cursor.fetchone()

        if result[0] > 0:  # มี bin_id อยู่แล้ว -> อัปเดตข้อมูล
            cursor.execute("""
                UPDATE tbl_bin_detail
                SET bottle_amount = %s,
                    can_amount = %s,
                    papercup_amount = %s,
                    others_amount = %s,
                    amount_time = %s
                WHERE bin_id = %s
            """, (bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others, datetime.now(), bin_id))
            print(f"Updated bin level data for bin_id {bin_id}")

        else:  # ไม่มี bin_id -> เพิ่มข้อมูลใหม่

            cursor.execute(
                """
                INSERT INTO tbl_bin (bin_id, bin_status)
                VALUES (%s, %s)
                """,
                (bin_id, 0)
            )
            print(f"Inserted new bin_id {bin_id} with bin_status 0")

            cursor.execute("""
                INSERT INTO tbl_bin_detail (bin_id, bottle_amount, can_amount, papercup_amount, others_amount, amount_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bin_id, bin_level_bottle, bin_level_can, bin_level_papercup, bin_level_others, datetime.now()))
            print(f"Inserted new bin level data for bin_id {bin_id}")

        # บันทึกการเปลี่ยนแปลงในฐานข้อมูล
        db.commit()

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")

    finally:
        cursor.close()
        db.close()

def save_bin_status(bin_id, bin_status):
    """
    บันทึกหรืออัปเดตสถานะ bin_status ในตาราง tbl_bin
    """
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return False

    cursor = db.cursor()

    try:
        # ตรวจสอบว่ามี bin_id อยู่ใน tbl_bin หรือไม่
        cursor.execute("SELECT COUNT(*) FROM tbl_bin WHERE bin_id = %s", (bin_id,))
        result = cursor.fetchone()

        if result[0] > 0:
            # หากมี bin_id อยู่แล้ว ให้อัปเดต bin_status
            cursor.execute(
                """
                UPDATE tbl_bin
                SET bin_status = %s
                WHERE bin_id = %s
                """,
                (bin_status, bin_id)
            )
            #print(f"Updated bin_status for bin_id {bin_id} to {bin_status}")
        else:
            # หากไม่มี bin_id ให้เพิ่มแถวใหม่ในตาราง
            cursor.execute(
                """
                INSERT INTO tbl_bin (bin_id, bin_status)
                VALUES (%s, %s)
                """,
                (bin_id, bin_status)
            )
            print(f"Inserted new bin_id {bin_id} with bin_status {bin_status}")

        # บันทึกการเปลี่ยนแปลงในฐานข้อมูล
        db.commit()
        return True

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        return False

    finally:
        cursor.close()
        db.close()



def get_bin_level(bin_id, column=None):
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return None

    cursor = db.cursor(pymysql.cursors.DictCursor)  # ใช้ DictCursor เพื่อให้ผลลัพธ์เป็น key-value

    try:
        if column:
            # ดึงข้อมูลเฉพาะคอลัมน์ที่ระบุ
            query = f"SELECT {column} FROM tbl_bin_detail WHERE bin_id = %s"
            cursor.execute(query, (bin_id,))
        else:
            # ดึงข้อมูลทั้งหมด
            query = "SELECT * FROM tbl_bin_detail WHERE bin_id = %s"
            cursor.execute(query, (bin_id,))

        result = cursor.fetchone()

        if result:
            print(f"Data retrieved for bin_id {bin_id}: {result}")
        else:
            print(f"No data found for bin_id {bin_id}")

        return result

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        return None

    finally:
        cursor.close()
        db.close()

def get_bin_status(bin_id):
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return None

    cursor = db.cursor()
    try:
        cursor.execute("SELECT bin_status FROM tbl_bin WHERE bin_id = %s", (bin_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # คืนค่า bin_status
        else:
            print(f"No status found for bin_id {bin_id}")
            return None

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return None

    finally:
        cursor.close()
        db.close()

def get_bin_details(bin_id):
    """ดึงข้อมูลปริมาณขยะตาม bin_id"""
    connection = get_database_connection()
    if not connection:
        return None

    cursor = connection.cursor()
    try:
        query = """
            SELECT bottle_amount, can_amount, papercup_amount, others_amount, amount_time
            FROM tbl_bin_detail
            WHERE bin_id = %s
            ORDER BY amount_time DESC
            LIMIT 1
        """
        cursor.execute(query, (bin_id,))
        return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error fetching bin details: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_garbage_history(bin_id, selected_date=None, date_type="day", garbage_type=None):
    """
    ดึงข้อมูลประวัติขยะจากฐานข้อมูล ตาม bin_id, วันที่ และประเภทขยะ
    - date_type: "day" -> yyyy-MM-dd, "month" -> yyyy-MM, "year" -> yyyy, "all" -> ไม่กำหนดช่วงเวลา
    - garbage_type: "bottle", "can", "papercup", "non_object" หรือ None (ทั้งหมด)
    """
    connection = get_database_connection()
    if connection is None:
        print("ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        return []

    cursor = connection.cursor()

    try:
        query = """
            SELECT garbage_id, garbage_img 
            FROM tbl_garbage 
            WHERE bin_id = %s
        """
        params = [bin_id]

        if selected_date:
            if date_type == "day":
                query += " AND DATE(garbage_date) = %s"
            elif date_type == "month":
                query += " AND DATE_FORMAT(garbage_date, '%%Y-%%m') = %s"
            elif date_type == "year":
                query += " AND YEAR(garbage_date) = %s"
            params.append(selected_date)

        if garbage_type:
            type_map = {
                "ขวด": "bottle",
                "กระป๋อง": "can",
                "แก้วกระดาษ": "papercup",
                "อื่นๆ": "non_object"
            }
            query += " AND garbage_type = %s"
            params.append(type_map.get(garbage_type, garbage_type))

        query += " ORDER BY garbage_id DESC"
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        return results

    except pymysql.MySQLError as e:
        print(f"Error fetching garbage history: {e}")
        return []
    finally:
        cursor.close()
        connection.close()



def save_bin_level_and_notify(bin_id, bin_level, bin_notify):
    """
    บันทึกหรืออัปเดตค่า bin_level และ bin_notify ลงใน tbl_bin
    """
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return False

    cursor = db.cursor()

    try:
        # ตรวจสอบว่ามี bin_id อยู่แล้วหรือไม่
        cursor.execute("SELECT COUNT(*) FROM tbl_bin WHERE bin_id = %s", (bin_id,))
        result = cursor.fetchone()

        if result[0] > 0:  # มี bin_id อยู่แล้ว -> อัปเดตข้อมูล
            cursor.execute("""
                UPDATE tbl_bin
                SET bin_level = %s, bin_notify = %s
                WHERE bin_id = %s
            """, (bin_level, bin_notify, bin_id))
            print(f"Updated bin_level and bin_notify for bin_id {bin_id}")

        else:  
            print(f"no data for BinID : {bin_id}")
        db.commit()
        return True

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        return False

    finally:
        cursor.close()
        db.close()

def get_bin_Alert(bin_id):
    """ดึงข้อมูล bin_level และ bin_notify จาก tbl_bin"""
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return None

    cursor = db.cursor(pymysql.cursors.DictCursor)  
    try:
        # ดึงข้อมูล bin_level และ bin_notify #
        query = "SELECT bin_level, bin_notify FROM tbl_bin WHERE bin_id = %s"
        cursor.execute(query, (bin_id,))
        result = cursor.fetchone()
        # if result:
        #     #print(f"Data retrieved for bin_id {bin_id}: {result}")
        # else:
        #     print(f"No data found for bin_id {bin_id}")
        return result

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        return None

    finally:
        cursor.close()
        db.close()

def get_bin_ids_with_location():
    """ดึง bin_id และ bin_location จากฐานข้อมูล"""
    connection = get_database_connection()
    if not connection:
        return []

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT bin_id, bin_location FROM tbl_bin")
        results = cursor.fetchall()
        return [{"bin_id": row[0], "bin_location": row[1]} for row in results]
    except pymysql.MySQLError as e:
        print(f"Error fetching bin IDs and locations: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_bin():
    connection = get_database_connection()
    if not connection:
        return []

    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        query = "SELECT bin_id, bin_location, bin_status FROM tbl_bin"
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except pymysql.MySQLError as e:
        print(f"Error fetching bin details: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_bin_location(bin_id):
    """ดึง Location ปัจจุบันของ Bin ID จากฐานข้อมูล"""
    connection = get_database_connection()
    if not connection:
        return ""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT bin_location FROM tbl_bin WHERE bin_id = %s", (bin_id,))
        result = cursor.fetchone()
        return result[0] if result else ""
    finally:
        cursor.close()
        connection.close()

def update_bin_location(bin_id, new_location):
    """อัปเดต Location ใหม่ในฐานข้อมูล"""
    connection = get_database_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE tbl_bin SET bin_location = %s WHERE bin_id = %s", (new_location, bin_id))
        connection.commit()
        return True
    except pymysql.MySQLError as e:
        print(f"Error updating bin location: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def delete_bin(bin_id):
    """ลบข้อมูลถังขยะและข้อมูลที่เกี่ยวข้องทั้งหมดในฐานข้อมูล"""
    connection = get_database_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        # ลบข้อมูลที่เกี่ยวข้องกับ bin_id
        cursor.execute("DELETE FROM tbl_bin_detail WHERE bin_id = %s", (bin_id,))
        cursor.execute("DELETE FROM tbl_garbage WHERE bin_id = %s", (bin_id,))
        cursor.execute("DELETE FROM tbl_report WHERE bin_id = %s", (bin_id,))
        cursor.execute("DELETE FROM tbl_bin WHERE bin_id = %s", (bin_id,))
        connection.commit()
        print(f"Deleted all data related to bin_id {bin_id}")
        return True
    except pymysql.MySQLError as e:
        print(f"Error deleting bin_id {bin_id}: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

##########################
### NotificationWindow ###
##########################

def save_report(binid):
    """
    บันทึกข้อมูลขยะลงใน tbl_garbage โดยใช้ machine_id เป็น bin_id
    """
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return

    cursor = db.cursor()
    status = 0
    try:
        # คำสั่ง SQL สำหรับการบันทึกข้อมูล
        cursor.execute("""
            INSERT INTO tbl_report (bin_id, report_date, report_status)
            VALUES (%s, %s, %s)
        """, (binid, datetime.now(), status))

        db.commit()

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
    
    finally:
        cursor.close()
        db.close()

def handle_report_status(bin_id, status):
    """
    จัดการสถานะของ report:
    - สร้าง report ใหม่หากไม่มีข้อมูล
    - อัปเดตสถานะพร้อมแก้ไข `report_edit_date` หากมีข้อมูลอยู่แล้ว
    """
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return

    cursor = db.cursor()

    try:
        # ตรวจสอบ report ล่าสุดของ bin_id
        cursor.execute("""
            SELECT report_id, report_status, report_date FROM tbl_report
            WHERE bin_id = %s
            ORDER BY report_date DESC
            LIMIT 1
        """, (bin_id,))
        result = cursor.fetchone()

        if result:
            report_id, current_status, report_date = result
            if status == 0 and current_status == 1:
                # หากขาดการเชื่อมต่ออีกครั้ง -> สร้างใหม่
                cursor.execute("""
                    INSERT INTO tbl_report (bin_id, report_date, report_status)
                    VALUES (%s, %s, %s)
                """, (bin_id, datetime.now(), status))
                print(f"Created new report for bin_id {bin_id} with status {status}")
            else:
                # อัปเดต report ล่าสุด
                cursor.execute("""
                    UPDATE tbl_report
                    SET report_status = %s, report_edit_date = %s
                    WHERE report_id = %s
                """, (status, datetime.now(), report_id))
                print(f"Updated report_id {report_id} for bin_id {bin_id} to status {status}")
                
                #location = get_bin_location(bin_id)
                #sendmessage("admin", f"ถังขยะที่ : {bin_id} - {location} กลับมาทำงานอีกครั้ง")
        else:
            # หากไม่มี report -> สร้างใหม่
            cursor.execute("""
                INSERT INTO tbl_report (bin_id, report_date, report_status)
                VALUES (%s, %s, %s)
            """, (bin_id, datetime.now(), status))
            print(f"Created new report for bin_id {bin_id} with status {status}")

        db.commit()

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")

    finally:
        cursor.close()
        db.close()


def get_reports():
    db = get_database_connection()
    if not db:
        return []

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM tbl_report ORDER BY report_id DESC")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def update_report_message(report_id, message):
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return False

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE tbl_report
            SET report_message = %s
            WHERE report_id = %s
        """, (message, report_id))

        db.commit()
        print(f"Updated report_message for report_id {report_id}")
        return True

    except pymysql.MySQLError as e:
        print(f"Error updating report_message: {e}")
        return False

    finally:
        cursor.close()
        db.close()
        
def delete_report(report_id):
    """ลบรายงานจาก tbl_report ตาม report_id"""
    db = get_database_connection()
    if not db:
        return False

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM tbl_report WHERE report_id = %s", (report_id,))
        db.commit()
        print(f"Deleted report with ID {report_id}")
        return True
    except pymysql.MySQLError as e:
        print(f"Error deleting report: {e}")
        return False
    finally:
        cursor.close()
        db.close()




def get_bin_level_location(bin_id):
    db = get_database_connection()
    if not db:
        print("Failed to connect to the database.")
        return None

    cursor = db.cursor(pymysql.cursors.DictCursor)  # ใช้ DictCursor เพื่อให้ผลลัพธ์เป็น key-value

    try:
        # ดึงข้อมูลจาก tbl_bin_detail และ tbl_bin
        query = """
            SELECT 
                b.bin_location,
                d.bottle_amount AS bottle, 
                d.can_amount AS can, 
                d.papercup_amount AS paper_cup, 
                d.others_amount AS other 
            FROM tbl_bin_detail d
            JOIN tbl_bin b ON d.bin_id = b.bin_id
            WHERE d.bin_id = %s
        """
        cursor.execute(query, (bin_id,))
        result = cursor.fetchone()

        if result:
            print(f"Data retrieved for bin_id {bin_id}: {result}")
        else:
            print(f"No data found for bin_id {bin_id}")

        return result

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        return None

    finally:
        cursor.close()
        db.close()


##############################################
################# TELEGRAM ###################
##############################################

def save_user_sql(chat_id, name, role="user"):
    db = get_database_connection()
    if not db:
        return

    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM tbl_users WHERE chat_id = %s", (chat_id,))
        exists = cursor.fetchone()[0]

        if exists > 0:
            cursor.execute("""
                UPDATE tbl_users SET name = %s, role = %s WHERE chat_id = %s
            """, (name, role, chat_id))
            print(f"Updated user {chat_id}: name={name}, role={role}")
        else:
            cursor.execute("""
                INSERT INTO tbl_users (chat_id, name, role) VALUES (%s, %s, %s)
            """, (chat_id, name, role))
            print(f"Inserted new user {chat_id}: name={name}, role={role}")

        db.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        db.close()


def get_user_info_sql(chat_id):
    db = get_database_connection()
    if not db:
        return {}

    cursor = db.cursor(pymysql.cursors.DictCursor) 
    try:
        cursor.execute("SELECT * FROM tbl_users WHERE chat_id = %s", (chat_id,))
        result = cursor.fetchone()
        return result if result else {}

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return {}

    finally:
        cursor.close()
        db.close()

def get_user_role_sql(chat_id):
    user_info = get_user_info_sql(chat_id)
    return user_info.get("role", "user")

def get_all_users():
    db = get_database_connection()
    if not db:
        return []

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT chat_id, role FROM tbl_users")
        return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def get_all_user_names():
    """ดึงรายชื่อผู้ใช้ทั้งหมดจากฐานข้อมูล"""
    db = get_database_connection()
    if not db:
        return []

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT name, role FROM tbl_users ORDER BY role DESC, name ASC")
        return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def delete_user_by_name(name):
    """ลบผู้ใช้จากฐานข้อมูลตามชื่อ"""
    db = get_database_connection()
    if not db:
        return False

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM tbl_users WHERE name = %s", (name,))
        db.commit()
        print(f"Deleted user with name {name}")
        return True
    except pymysql.MySQLError as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        cursor.close()
        db.close()

def get_garbage_summary(date_type="day"):
    """ ดึงข้อมูลปริมาณขยะรวม ตามวัน, เดือน, ปี """
    db = get_database_connection()
    if not db:
        return None

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        if date_type == "day":
            date_format = "%Y-%m-%d"
            date_query = "CURDATE()"  # ใช้วันปัจจุบัน
        elif date_type == "month":
            date_format = "%Y-%m"
            date_query = "DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m')"  # ใช้เดือนที่แล้ว
        elif date_type == "year":
            date_format = "%Y"
            date_query = "DATE_FORMAT(NOW() - INTERVAL 1 YEAR, '%Y')"  # ใช้ปีที่แล้ว
        else:
            return None

        query = f"""
            SELECT garbage_type, COUNT(*) AS count
            FROM tbl_garbage
            WHERE DATE_FORMAT(garbage_date, '{date_format}') = {date_query}
            GROUP BY garbage_type
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return result
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        db.close()
