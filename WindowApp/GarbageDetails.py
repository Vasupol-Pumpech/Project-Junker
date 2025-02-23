import json
import os
import sys
import pymysql
import locale
import mqtt_config
from PyQt5.QtCore import QTimer,QLocale,pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap,QColor
from PyQt5.QtWidgets import (QApplication, QCalendarWidget,
                             QComboBox, QDialog, QFrame,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QSizePolicy, QSlider,
                             QVBoxLayout,QListWidgetItem,QSpacerItem)
                            

from sql import get_bin_ids_with_location, get_bin_details, get_garbage_history, save_bin_level_and_notify, get_bin_Alert, get_bin_status, delete_garbage, delete_all_garbage
from Telegram import sendmessageto
from TrashDetailWindow import TrashDetailWindow
from NotiWindow import NotificationsPopup
from Aboutus import AboutUsWindow  
class GarbageDetailsWindow(QMainWindow):
    garbage_updated = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("pic/bin.png"))
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
        sendmessageto("admin","วินโด้แอปพลิเคชันเริ่มทำงานอีกครั้ง")
        self.setWindowTitle("ระบบติดตามถังแยกขยะอัตโนมัติ")  
        self.setGeometry(100, 100, 1200, 700)
        self.selected_date = None
        self.garbage_updated.connect(self.load_garbage_history)



        #loop 
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.load_garbage_history)
        self.timer.timeout.connect(self.get_garbage_level)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_sliders)
        self.timer2.start(60000)

        # ค่าตั้งต้น
        self.full_threshold = 0
        self.alert_threshold_percentage = 0
        
        # Layout หลัก 
        main_layout = QVBoxLayout() 
        middle_layout = QGridLayout()

        
        # ส่วนบน: Dropdown และปุ่มแจ้งเตือน
        header_layout = QHBoxLayout()

        self.status_label = QLabel("สถานะ: ไม่ทราบ")
        self.status_label.setStyleSheet("font-size: 16px; color: gray;")
        header_layout.addWidget(self.status_label)

        # สร้าง dropdown_menu
        self.dropdown_menu = QComboBox()
        self.load_bin_ids()
        
        self.dropdown_menu.currentIndexChanged.connect(self.on_id_change)
    
        header_layout.addWidget(self.dropdown_menu)


        add_edit_button = QPushButton("รายละเอียด")
        add_edit_button.setStyleSheet("background-color: orange; font-size: 14px;")
        add_edit_button.clicked.connect(self.open_trash_detail_window)  # เปิดหน้าต่าง TrashDetailWindow
        header_layout.addWidget(add_edit_button)
        
        add_edit_button.setStyleSheet
        ("""
        background-color: orange;
        font-size: 14px;
        color: white;
        border-radius: 5px;
        padding: 10px;
        """)
        
       # ปุ่มกระดิ่ง
        notification_button = QPushButton()
        pixmap = QPixmap("pic/bell.png")  # โหลดภาพ bell.png
        scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # ปรับขนาดภาพ
        notification_button.setIcon(QIcon(scaled_pixmap))  # ใช้ภาพที่ปรับขนาดเป็นไอคอน
        notification_button.setIconSize(scaled_pixmap.size())  # กำหนดขนาดไอคอนให้ตรงกับภาพที่ปรับ
        notification_button.setFixedSize(40, 40)  # ขนาดปุ่มใหญ่กว่าภาพเล็กน้อย
        notification_button.setStyleSheet("border: none;")  # เอาเส้นขอบออก
        header_layout.addWidget(notification_button)
        notification_button.clicked.connect(self.open_notifications_popup)

        # ปุ่มปฏิทิน
        calendar_button = QPushButton()
        pixmap = QPixmap("pic/calendar.png")  # โหลดภาพ
        scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # ปรับขนาดภาพ
        calendar_button.setIcon(QIcon(scaled_pixmap))  # ใช้ภาพที่ปรับขนาดเป็นไอคอน
        calendar_button.setIconSize(scaled_pixmap.size())  # กำหนดขนาดไอคอนให้ตรงกับภาพที่ปรับ
        calendar_button.setFixedSize(40, 40)  # ขนาดของปุ่ม (ใหญ่กว่าภาพเล็กน้อย)
        calendar_button.setStyleSheet("border: none;")  # เอาเส้นขอบออก
        calendar_button.clicked.connect(self.show_calendar_popup)  # เชื่อมต่อฟังก์ชัน
        header_layout.addWidget(calendar_button)

        # ปุ่มเกี่ยวกับเรา
        about_button = QPushButton()
        pixmap = QPixmap("pic/info.png")  # โหลดภาพจากโฟลเดอร์ pic/
        scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)  
        about_button.setIcon(QIcon(scaled_pixmap))  
        about_button.setIconSize(scaled_pixmap.size())  
        about_button.setFixedSize(40, 40)  
        about_button.setStyleSheet("border: none;")  
        about_button.clicked.connect(self.open_about_us)
        header_layout.addWidget(about_button)


        main_layout.addLayout(header_layout)



        # ส่วนกลาง: กราฟวงกลม, รูปขยะ, หลอดแสดงปริมาณขยะ
        middle_layout = QGridLayout()

        # ประวัติการทิ้งขยะ
        history_frame = QFrame()
        history_frame.setFrameShape(QFrame.Box)
        history_frame.setFixedWidth(350)
        history_layout = QVBoxLayout(history_frame)

        # Label ของหัวข้อ
        self.history_label = QLabel("ประวัติการทิ้งขยะ:")
        history_layout.addWidget(self.history_label)

        # **เพิ่ม QComboBox สำหรับตัวกรองประเภทขยะ**
        self.filter_label = QLabel("กรองประเภทขยะ:")
        history_layout.addWidget(self.filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ทั้งหมด", "ขวด", "กระป๋อง", "แก้วกระดาษ", "อื่นๆ"])
        self.filter_combo.currentIndexChanged.connect(self.load_garbage_history)  # โหลดใหม่เมื่อเปลี่ยน
        history_layout.addWidget(self.filter_combo)

        # QListWidget สำหรับแสดงรายการรูปภาพ
        self.history_list = QListWidget()
        self.history_list.currentItemChanged.connect(self.display_images)
        history_layout.addWidget(self.history_list)

        # 
        button_layout = QHBoxLayout()

        self.delete_selected_button = QPushButton("ลบขยะที่เลือก")
        self.delete_selected_button.setStyleSheet("background-color: red; color: white; font-size: 14px;")
        self.delete_selected_button.clicked.connect(self.delete_selected_garbage)
        button_layout.addWidget(self.delete_selected_button)

        self.delete_all_button = QPushButton("ลบขยะทั้งหมด")
        self.delete_all_button.setStyleSheet("background-color: darkred; color: white; font-size: 14px;")
        self.delete_all_button.clicked.connect(self.delete_all_garbage_in_bin)
        button_layout.addWidget(self.delete_all_button)

        history_layout.addLayout(button_layout) 


        # เพิ่ม `history_frame` ลงใน layout หลัก
        middle_layout.addWidget(history_frame, 0, 2)

        # โหลดรายการรูปภาพ
        self.load_garbage_history()
        middle_layout.addWidget(history_frame, 0, 2)

        # กราฟวงกลม
        pie_chart_frame = QFrame()
        pie_chart_frame.setFrameShape(QFrame.Box)
        pie_chart_layout = QVBoxLayout(pie_chart_frame)

        self.pie_chart = self.create_pie_chart()
        pie_chart_view = QChartView(self.pie_chart)
        pie_chart_view.setMinimumSize(550, 300)
        pie_chart_layout.addWidget(pie_chart_view)

        middle_layout.addWidget(pie_chart_frame, 0, 0)

        # รูปภาพขยะ
        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.Box)
        image_layout = QVBoxLayout(image_frame)

        # Label สำหรับข้อความ
        image_label = QLabel("รูปขยะ")
        image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(image_label)  # เพิ่มข้อความที่ด้านบน

        # QLabel สำหรับแสดงภาพ
        self.image_display = QLabel()
        self.image_display.setScaledContents(True)
        self.image_display.setFixedSize(300, 300)
        image_layout.addWidget(self.image_display)  # เพิ่มรูปที่อยู่กลาง

        # ตั้งค่าการจัดเรียงให้ข้อความอยู่บนสุด และรูปอยู่กึ่งกลาง
        image_layout.setAlignment(image_label, Qt.AlignTop)  # ให้ข้อความอยู่ด้านบน
        image_layout.setAlignment(self.image_display, Qt.AlignCenter)  # ให้รูปอยู่ตรงกลาง

        # เพิ่มกรอบที่มีรูปภาพและข้อความลงใน layout หลัก
        middle_layout.addWidget(image_frame, 0, 3)
        main_layout.addLayout(middle_layout)
        
        main_widget =QFrame()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # ส่วนล่างสุด: 2 คอลัมน์
        bottom_layout = QHBoxLayout()
        # คอลัมน์ซ้าย: ไอคอน, Progress Bars, และข้อความ %
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        left_layout = QHBoxLayout(left_frame)  # จัด Layout แนวนอนในกรอบซ้าย

        # สร้าง Progress Bars พร้อมไอคอนและข้อความเปอร์เซ็นต์
        self.progress_bars = []
        self.labels = []
        icons = ["bottle.png", "can.png", "papercup.png", "other.png"]  # ไฟล์ไอคอน
        types_of_garbage = ["ขวด", "กระป๋อง", "แก้วกระดาษ", "อื่นๆ"]
        
        for i, garbage_type in enumerate(types_of_garbage):
            vertical_layout = QVBoxLayout()  # จัด Layout แนวตั้งสำหรับแต่ละรายการ

            # เพิ่มไอคอน
            icon_label = QLabel()
            icon_path = f"pic/{icons[i]}"
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                icon_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio))  # ปรับขนาดไอคอน
            else:
                icon_label.setText("X")  
            vertical_layout.addWidget(icon_label, alignment=Qt.AlignCenter)

            # เพิ่มข้อความประเภทขยะใต้ไอคอน
            vertical_layout.addSpacing(10) 
            type_label = QLabel(garbage_type)
            type_label.setAlignment(Qt.AlignCenter)
            type_label.setStyleSheet("font-size: 14px; color: black;")
            vertical_layout.addWidget(type_label, alignment=Qt.AlignCenter)

            # เพิ่ม Progress Bar แนวตั้ง
            vertical_layout.addSpacing(10)
            progress_bar = QProgressBar()
            progress_bar.setOrientation(Qt.Vertical)
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setValue(0)
            progress_bar.setFixedSize(50, 200)
            self.progress_bars.append(progress_bar)
            vertical_layout.addWidget(progress_bar, alignment=Qt.AlignCenter)

            # เพิ่มข้อความเปอร์เซ็นต์
            vertical_layout.addSpacing(10) 
            percentage_label = QLabel("0%")
            percentage_label.setAlignment(Qt.AlignCenter)
            percentage_label.setStyleSheet("font-size: 14px; color: black;")
            self.labels.append(percentage_label)
            vertical_layout.addWidget(percentage_label, alignment=Qt.AlignCenter)

            # เพิ่ม SpacerItem เพื่อสร้างระยะห่างคงที่ระหว่างแต่ละ Bar
            spacer = QSpacerItem(100, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
            vertical_layout.addItem(spacer)

            # เพิ่ม Layout ของแต่ละรายการลงใน Layout หลัก
            left_layout.addLayout(vertical_layout)

        bottom_layout.addWidget(left_frame)  # เพิ่มคอลัมน์ซ้ายใน Layout

        # คอลัมน์ขวา: Slider Bars
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.Box)
        slider_layout = QVBoxLayout(slider_frame)

        slider_full_label = QLabel("ระดับการเต็มของถังขยะ:")
        slider_full_label.setStyleSheet("font-size: 14px;")
        slider_layout.addWidget(slider_full_label)

        self.slider_full = QSlider(Qt.Horizontal)
        self.slider_full.setMinimum(1)  # ค่าเริ่มต้นขั้นต่ำ
        self.slider_full.setMaximum(100)  # ค่าเริ่มต้นสูงสุด
        self.slider_full.setValue(50)  # ตั้งค่าพื้นฐาน
        self.slider_full.setTickInterval(1)  # กำหนดช่วงการเลื่อนให้เป็นจำนวนเต็ม
        self.slider_full.setSingleStep(1)  # เลื่อนทีละ 1
        slider_layout.addWidget(self.slider_full)

        self.slider_full_value = QLineEdit(str(self.full_threshold))
        self.slider_full_value.setValidator(QIntValidator(1, 100))
        self.slider_full_value.setFixedWidth(50)
        self.slider_full_value.setStyleSheet("font-size: 16px;")
        slider_layout.addWidget(self.slider_full_value)

        self.slider_full.valueChanged.connect(self.update_slider_full)

        # Slider การแจ้งเตือน
        slider_alert_label = QLabel("ระดับแจ้งเตือน:")
        slider_alert_label.setStyleSheet("font-size: 14px;")
        slider_layout.addWidget(slider_alert_label)

        self.slider_alert_percentage = QSlider(Qt.Horizontal)
        self.slider_alert_percentage.setMinimum(0)
        self.slider_alert_percentage.setMaximum(100)
        self.slider_alert_percentage.setValue(20)
        self.slider_alert_percentage.setTickInterval(1) 
        self.slider_alert_percentage.setSingleStep(1)
        slider_layout.addWidget(self.slider_alert_percentage)

        self.slider_alert_value = QLineEdit(str(self.alert_threshold_percentage))
        self.slider_alert_value.setValidator(QIntValidator(0, 100))
        self.slider_alert_value.setFixedWidth(50)
        self.slider_alert_value.setStyleSheet("font-size: 16px;")
        slider_layout.addWidget(self.slider_alert_value)

        self.slider_alert_percentage.valueChanged.connect(self.update_alert_threshold_label)

        self.update_sliders()
        
        # ปุ่มบันทึก
        slider_layout.addSpacing(20)
        save_button = QPushButton("บันทึก")
        save_button.setStyleSheet("background-color: green; color: white; font-size: 14px;")
        save_button.clicked.connect(self.save_bin_level)
        slider_layout.addWidget(save_button)

        bottom_layout.addWidget(slider_frame) 

        main_layout.addLayout(bottom_layout)

    def load_bin_ids(self):
        """โหลด bin_id และ bin_location จากฐานข้อมูล และตั้งค่า default เป็น ID 1"""
        bins = get_bin_ids_with_location()  # ดึงข้อมูลถังขยะจากฐานข้อมูล
        new_items = {bin_data["bin_id"]: bin_data["bin_location"] for bin_data in bins}

        # กำหนดค่าเริ่มต้นเป็น ID 1
        selected_bin_id = self.dropdown_menu.currentData() or 1

        # เปรียบเทียบข้อมูลเดิมกับข้อมูลใหม่
        current_items = {
            self.dropdown_menu.itemData(i): self.dropdown_menu.itemText(i)
            for i in range(self.dropdown_menu.count())
        }

        # หากข้อมูลเปลี่ยนแปลง ให้รีเฟรช dropdown_menu
        if new_items != current_items:
            self.dropdown_menu.blockSignals(True)
            self.dropdown_menu.clear()

            # เพิ่มรายการถังขยะใน dropdown_menu
            for bin_id, bin_location in new_items.items():
                self.dropdown_menu.addItem(f"หมายเลขถังขยะ : {bin_id} - {bin_location}", bin_id)

            # หากไม่มีข้อมูลถังขยะในฐานข้อมูล
            if not new_items:
                print("No bins available in database.")
                self.dropdown_menu.addItem("No bins available", 1)
            self.dropdown_menu.blockSignals(False)

        # ตั้งค่า selected_bin_id หากยังมีอยู่
        if selected_bin_id in new_items:
            index = list(new_items.keys()).index(selected_bin_id)
            self.dropdown_menu.setCurrentIndex(index)
        elif new_items:
            # หาก selected_bin_id ไม่มีอยู่ ให้เลือกถังขยะแรกในรายการ
            self.dropdown_menu.setCurrentIndex(0)
            print("Reset to first bin in the list.")
        else:
            # หากไม่มีถังขยะเลย ให้แสดงข้อความใน dropdown
            self.dropdown_menu.clear()
            self.dropdown_menu.addItem("No bins available", 1)
        
 
    def get_garbage_level(self):
        """อัปเดต UI ด้วยข้อมูล bin ที่เลือก"""
        selected_bin_id = self.dropdown_menu.currentData()
        if not selected_bin_id:
            print("กรุณาเลือกถังขยะ")
            return

        # ดึงข้อมูล bin_level และ bin_notify จากฐานข้อมูล
        bin_alert_data = get_bin_Alert(selected_bin_id)  # ใช้ฟังก์ชันจาก sql.py
        if not bin_alert_data:
            print(f"ไม่สามารถดึงข้อมูล bin_level และ bin_notify สำหรับ bin_id {selected_bin_id}")
            return

        # ตั้งค่าการแจ้งเตือนและระดับเต็ม
        full_threshold = bin_alert_data.get("bin_level", 0)
        alert_threshold = bin_alert_data.get("bin_notify", 0)

        # ดึงข้อมูลปริมาณขยะจาก tbl_bin_detail
        bin_details = get_bin_details(selected_bin_id)
        if not bin_details:
            print(f"ไม่มีข้อมูล bin_details สำหรับ bin_id {selected_bin_id}")
            return

        bottle_amount, can_amount, papercup_amount, others_amount, amount_time = bin_details
        total_values = [bottle_amount, can_amount, papercup_amount, others_amount]

        # อัปเดต UI (โปรเกรสบาร์และข้อความ)
        for i, progress_bar in enumerate(self.progress_bars):
            value = total_values[i]
            progress_bar.setValue(value)
            progress_bar.setTextVisible(False)

            # แสดงเปอร์เซ็นต์ใต้ Progress Bar
            self.labels[i].setText(f"{value}%")

            # เปลี่ยนสีของ Progress Bar
            if value >= full_threshold:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif value >= alert_threshold:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")

        # อัปเดตกราฟวงกลม
        self.update_pie_chart(total_values)


    def load_garbage_history(self):
        """โหลดรายการรูปภาพจากฐานข้อมูลตาม bin_id ที่เลือก และประเภทขยะ"""
        selected_bin_id = self.dropdown_menu.currentData()  # ดึง bin_id ที่เลือก
        selected_filter = self.filter_combo.currentText()  # ดึงค่าที่เลือกจาก ComboBox
        if selected_filter == "ทั้งหมด":
            selected_filter = None  # ไม่ต้องกรองประเภท

        if not selected_bin_id:
            self.history_list.addItem("กรุณาเลือกถังขยะ")
            self.update_history_label(0)  # แสดงจำนวน 0
            return

        # ตรวจสอบรูปแบบของ selected_date และกำหนด date_type
        if self.selected_date:
            if len(self.selected_date) == 10:  # yyyy-MM-dd
                date_type = "day"
            elif len(self.selected_date) == 7:  # yyyy-MM
                date_type = "month"
            elif len(self.selected_date) == 4:  # yyyy
                date_type = "year"
            else:
                date_type = "all"
        else:
            date_type = "all"

        # ดึงข้อมูลจากฐานข้อมูล
        results = get_garbage_history(selected_bin_id, self.selected_date, date_type, selected_filter)

        # บันทึกไอเทมที่เลือกไว้ก่อนโหลดข้อมูลใหม่
        selected_item = self.history_list.currentItem()
        selected_data = selected_item.data(Qt.UserRole) if selected_item else None

        self.history_list.clear()

        if results:
            for garbage_id, garbage_img in results:
                if os.path.exists(garbage_img):
                    item = QListWidgetItem(f"{os.path.basename(garbage_img)}")
                    item.setData(Qt.UserRole, garbage_img)
                    self.history_list.addItem(item)
                    
                    # เลือกไอเทมเดิมกลับมา (ถ้ายังอยู่ในรายการ)
                    if selected_data and selected_data == garbage_img:
                        self.history_list.setCurrentItem(item)
                else:
                    self.history_list.addItem(f"ID {garbage_id}: ไฟล์ไม่พบ")


            # อัปเดตข้อความในหัวข้อ "ประวัติการทิ้งขยะ"
            self.update_history_label(len(results))
        else:
            self.history_list.addItem(f"ไม่มีข้อมูลสำหรับ ถังขยะที่ : {selected_bin_id}")
            self.update_history_label(0)



    def display_images(self, current, previous):
        if current:
            image_path = current.data(Qt.UserRole)
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.image_display.setPixmap(pixmap)
            else:
                self.image_display.clear()
            
    def open_notifications_popup(self):
        bin_info = []

        popup = NotificationsPopup(bin_info, self)
        popup.exec_()

    def open_trash_detail_window(self):
        """เปิดหน้าต่าง TrashDetailWindow"""
        self.trash_detail_window = TrashDetailWindow()
        self.trash_detail_window.finished.connect(self.load_bin_ids)
        self.trash_detail_window.exec_() 
    
    def open_about_us(self):
        """เปิดหน้าต่างเกี่ยวกับเรา"""
        self.about_us_window = AboutUsWindow(self)
        self.about_us_window.exec_()


    def reset_date(self, dialog):
        """รีเซ็ตวันที่และแสดงประวัติทั้งหมด"""
        self.selected_date = None
        self.load_garbage_history() 
        dialog.reject()

    def update_history_label(self, total_count):
        """อัปเดตข้อความในหัวข้อประวัติการทิ้งขยะ"""
        if self.selected_date:  
            self.history_label.setText(f"ประวัติการทิ้งขยะ (จำนวน {total_count} ชิ้น) - วันที่เลือก: {self.selected_date}")
        else:  
            self.history_label.setText(f"ประวัติการทิ้งขยะ (จำนวน {total_count} ชิ้น) - แสดงทั้งหมด")
    
    def show_calendar_popup(self):
        """แสดงป๊อปอัพปฏิทิน ให้เลือก วัน / เดือน / ปี"""
        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle("ปฏิทินขยะ")
        calendar_dialog.setGeometry(300, 300, 350, 400)
        calendar_dialog.setWindowIcon(QIcon("pic/calendar.png"))

        layout = QVBoxLayout(calendar_dialog)

        # QCalendarWidget สำหรับเลือกวัน / เดือน / ปี
        self.calendar = QCalendarWidget(calendar_dialog)
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)


        # ปุ่มเลือกวัน / เดือน / ปี
        button_layout = QHBoxLayout()

        day_button = QPushButton("เลือกวัน")
        day_button.clicked.connect(lambda: self.select_date("day", calendar_dialog))
        button_layout.addWidget(day_button)

        month_button = QPushButton("เลือกเดือน")
        month_button.clicked.connect(lambda: self.select_date("month", calendar_dialog))
        button_layout.addWidget(month_button)

        year_button = QPushButton("เลือกปี")
        year_button.clicked.connect(lambda: self.select_date("year", calendar_dialog))
        button_layout.addWidget(year_button)

        # ปุ่มแสดงทั้งหมด
        show_all_button = QPushButton("แสดงทั้งหมด")
        show_all_button.clicked.connect(lambda: self.reset_date(calendar_dialog))
        button_layout.addWidget(show_all_button)

        # ปุ่มยกเลิก
        cancel_button = QPushButton("ยกเลิก")
        cancel_button.clicked.connect(calendar_dialog.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # แสดงป๊อปอัพปฏิทิน
        if calendar_dialog.exec_() == QDialog.Accepted:
            self.load_garbage_history()  # โหลดข้อมูลใหม่หลังเลือกวันที่

    def select_date(self, option, dialog):
        """บันทึกช่วงเวลาที่เลือก (วัน / เดือน / ปี)"""
        selected_date = self.calendar.selectedDate()

        if option == "day":
            self.selected_date = selected_date.toString("yyyy-MM-dd")
        elif option == "month":
            self.selected_date = selected_date.toString("yyyy-MM")
        elif option == "year":
            self.selected_date = selected_date.toString("yyyy")

        # แปลงเลขไทยเป็นเลขอารบิก
        thai_to_arabic = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
        self.selected_date = self.selected_date.translate(thai_to_arabic)

        print(f"✅ เลือกช่วงเวลา (หลังแปลง): {self.selected_date}")

        dialog.accept()
        self.load_garbage_history()  # โหลดข้อมูลใหม่หลังจากเลือก



    def reset_date(self, dialog):
        """รีเซ็ตการเลือกวันที่ และแสดงข้อมูลทั้งหมด"""
        self.selected_date = None
        print("รีเซ็ตวันที่: แสดงข้อมูลทั้งหมด")
        self.load_garbage_history()
        dialog.reject()

    def delete_selected_garbage(self):
        """ลบขยะที่เลือกจากรายการ"""
        selected_item = self.history_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกขยะที่ต้องการลบ")
            return

        garbage_img = selected_item.data(Qt.UserRole)

        # ยืนยันการลบ
        confirm = QMessageBox.question(
            self, "Confirm", f"คุณต้องการลบขยะนี้ใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            garbage_id = None
            results = get_garbage_history(self.dropdown_menu.currentData())
            for g_id, img in results:
                if img == garbage_img:
                    garbage_id = g_id
                    break

            if garbage_id and delete_garbage(garbage_id):
                QMessageBox.information(self, "Success", "ลบขยะสำเร็จ")
                self.load_garbage_history()
                self.history_list.clearSelection()  # ป้องกันการรีเฟรชแล้วหาย

            else:
                QMessageBox.critical(self, "Error", "ไม่สามารถลบขยะได้")


    def delete_all_garbage_in_bin(self):
        """ลบข้อมูลขยะทั้งหมดของถังขยะที่เลือก"""
        selected_bin_id = self.dropdown_menu.currentData()
        if not selected_bin_id:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกถังขยะก่อนลบข้อมูลทั้งหมด")
            return

        # ยืนยันการลบทั้งหมด
        confirm = QMessageBox.question(
            self, "Confirm", f"คุณต้องการลบข้อมูลขยะทั้งหมดของถังขยะ {selected_bin_id} หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if delete_all_garbage(selected_bin_id):
                QMessageBox.information(self, "Success", "ลบข้อมูลขยะทั้งหมดสำเร็จ")
                self.load_garbage_history()
            else:
                QMessageBox.critical(self, "Error", "ไม่สามารถลบข้อมูลขยะทั้งหมดได้")

    def update_slider_full(self, value):
        self.full_threshold = value
        self.slider_full_value.setText(str(value))

    def update_alert_threshold_label(self, value):
        self.alert_threshold_percentage = value
        self.slider_alert_value.setText(str(value))

    def save_bin_level(self):
        # ดึงค่า bin_id จาก dropdown
        selected_bin_id = self.dropdown_menu.currentData()
        if not selected_bin_id:
            QMessageBox.warning(self, "Error", "กรุณาเลือกถังขยะก่อนบันทึก")
            return

        # ตรวจสอบสถานะของถังขยะ
        bin_status = get_bin_status(selected_bin_id)
        if bin_status == 0:  # ถังขยะออฟไลน์
            QMessageBox.critical(self, "Error", "ถังขยะออฟไลน์ ไม่สามารถบันทึกได้")
            return

        # ดึงค่าจาก Sliders
        full_threshold = self.slider_full.value()
        alert_threshold = self.slider_alert_percentage.value()
        
        if alert_threshold >= full_threshold - 10:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "ระดับแจ้งเตือนต้องน้อยกว่าระดับการเต็มของถังขยะอย่างน้อย 10"
            )
            return  

        bin_level_topic = f"junker/{selected_bin_id}/level"
        payload = {
            "full_threshold": full_threshold,
            "alert_threshold": alert_threshold
        }

        # ส่งข้อมูลผ่าน MQTT
        try:
            mqtt_config.client.publish(bin_level_topic, json.dumps(payload), qos=1)
            print(f"MQTT Published: Topic={bin_level_topic}, Payload={payload}")
        except Exception as e:
            QMessageBox.critical(self, "MQTT Error", f"ไม่สามารถส่งข้อมูลผ่าน MQTT ได้: {str(e)}")
            return

        # บันทึกค่าไปยังฐานข้อมูล
        success = save_bin_level_and_notify(selected_bin_id, full_threshold, alert_threshold)
        if success:
            QMessageBox.information(self, "Success", "บันทึกข้อมูลเรียบร้อยแล้ว")
        else:
            QMessageBox.critical(self, "Error", "เกิดข้อผิดพลาดในการบันทึกข้อมูล")



    def load_icon(self, filename):
        return QIcon(f"pic/{filename}")

    def create_pie_chart(self):
        series = QPieSeries()
        series.append("ขยะที่ทิ้ง", 0)
        series.append("ขยะไม่ทิ้ง", 100)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("กราฟแสดงปริมาณขยะ")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        return chart

    def update_pie_chart(self, total_values):
        series = self.pie_chart.series()[0]
        series.clear()

        garbage_types = ["ขวด", "กระป๋อง", "แก้วกระดาษ", "อื่นๆ"]
        total_sum = sum(total_values)

        colors = [
            QColor("#2fb6eb"),  # ขวด
            QColor("#f94848"),  # กระป๋อง
            QColor("#e7eef9"),  # แก้วกระดาษ
            QColor("#92dd7a")   # อื่นๆ
        ]

        for i, value in enumerate(total_values):
            if total_sum > 0:  
                percentage = (value / total_sum) * 100
                slice = series.append(f"{garbage_types[i]} - {percentage:.1f}%", value)
                slice.setBrush(colors[i % len(colors)])  
            else:
                slice = series.append(f"{garbage_types[i]} - 0%", 0)
                slice.setBrush(colors[i % len(colors)])

        self.pie_chart.update()



    def update_sliders(self):
        """อัปเดต Slider และค่าข้อมูลจากฐานข้อมูล"""
        selected_bin_id = self.dropdown_menu.currentData()
        if not selected_bin_id:
            print("ไม่มี Bin ID ที่เลือก")
            return
        
        print(f"Selected Bin ID: {selected_bin_id}")
        
        # ใช้ฟังก์ชัน get_bin_Alert เพื่อดึง bin_level และ bin_notify
        bin_alert_data = get_bin_Alert(selected_bin_id)
        if bin_alert_data:
            bin_level = bin_alert_data.get('bin_level', 0) or 0
            bin_notify = bin_alert_data.get('bin_notify', 0) or 0

            # อัปเดต Slider และช่องข้อความ
            self.slider_full.setValue(bin_level)
            self.slider_full_value.setText(str(bin_level))
            self.slider_alert_percentage.setValue(bin_notify)
            self.slider_alert_value.setText(str(bin_notify))
        else:
            print(f"ไม่มีข้อมูลสำหรับ Bin ID: {selected_bin_id}")
            self.slider_full.setValue(0)
            self.slider_full_value.setText("0")
            self.slider_alert_percentage.setValue(0)
            self.slider_alert_value.setText("0")

    def on_id_change(self):
        self.load_garbage_history()
        self.get_garbage_level()
        self.update_status()
        self.update_sliders()
        return
    
    def update_status(self):
        """
        อัปเดตสถานะของถังขยะใน UI (Working/Offline) โดยอิงจาก bin_status
        """

        selected_bin_id = self.dropdown_menu.currentData()
        if not selected_bin_id:
            self.status_label.setText("สถานะ: ไม่ทราบ")
            self.status_label.setStyleSheet("font-size: 14px; color: gray;")
            return

        bin_status = get_bin_status(selected_bin_id)
        if bin_status is None:
            self.status_label.setText("สถานะ: ไม่ทราบ")
            self.status_label.setStyleSheet("font-size: 14px; color: gray;")
        elif bin_status == 1:
            self.status_label.setText("สถานะ: กำลังทำงาน")
            self.status_label.setStyleSheet("font-size: 14px; color: green;")
        else:
            self.status_label.setText("สถานะ: ขาดการเชื่อมต่อ")
            self.status_label.setStyleSheet("font-size: 14px; color: red;")

    
    def closeEvent(self, event):
        """เรียกใช้เมื่อหน้าต่างถูกปิด"""
        reply = QMessageBox.question(
            self,
            'Exit Application',
            "คุณต้องการปิดโปรแกรมหรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                sendmessageto("admin", "⚠️ วินโด้แอปพลิเคชันหยุดทำงานแล้ว!")
                print("แจ้งเตือนแอดมินสำเร็จ")
            except Exception as e:
                print(f"การแจ้งเตือนแอดมินล้มเหลว: {e}")
            event.accept()  
        else:
            event.ignore()  


if __name__ == "__main__":
    app = QApplication([])
    window = GarbageDetailsWindow()
    window.show()
    app.exec_()