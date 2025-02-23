from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QDateEdit, QComboBox, QHeaderView, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QDate, QLocale
from PyQt5.QtGui import QIcon
from sql import get_reports, get_bin_location, update_report_message, delete_report
from datetime import datetime    

class NotificationsPopup(QDialog):
    def __init__(self, bin_info=None, parent=None):
        super().__init__(parent)
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
        self.setWindowTitle("Notifications")
        self.setFixedSize(1200, 600)
        self.setWindowIcon(QIcon("pic/bell.png"))
        self.bin_info = bin_info

        # เก็บสถานะการเรียงลำดับ
        self.sort_order = {
            "วันที่เกิดปัญหา": True,  
            "วันที่แก้ไข": True      
        }

        # Layout หลัก
        layout = QVBoxLayout()

        # ตัวกรองในแถวเดียวกัน
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)
        filter_layout.setContentsMargins(0, 5, 0, 5)

        # ประเภทวันที่
        self.date_filter_type = QComboBox()
        self.date_filter_type.addItems(["วันที่เกิดปัญหา", "วันที่แก้ไขปัญหา"])
        self.date_filter_type.setFixedWidth(250)
        filter_layout.addWidget(QLabel("ประเภทวันที่:"))
        filter_layout.addWidget(self.date_filter_type)

        # ช่วงวันที่
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-1))
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setFixedWidth(120)

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setFixedWidth(120)

        filter_layout.addWidget(QLabel("ตั้งแต่:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("ถึง:"))
        filter_layout.addWidget(self.date_end)

        # สถานะ
        self.status_filter = QComboBox()
        self.status_filter.addItems(["ทั้งหมด", "แก้ไขแล้ว", "ยังไม่แก้ไข"])
        self.status_filter.setFixedWidth(120)
        filter_layout.addWidget(QLabel("สถานะ:"))
        filter_layout.addWidget(self.status_filter)

        # ปุ่ม Apply Filter
        self.apply_filter_button = QPushButton("ตกลง")
        self.apply_filter_button.setFixedWidth(100)
        self.apply_filter_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.apply_filter_button)

        # ปุ่ม Show All
        self.show_all_button = QPushButton("แสดงทั้งหมด")
        self.show_all_button.setFixedWidth(100)
        self.show_all_button.clicked.connect(self.load_report_data)
        filter_layout.addWidget(self.show_all_button)

        layout.addLayout(filter_layout)

        # ตารางแสดงข้อมูล
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(6)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table.setHorizontalHeaderLabels([
            "หมายเลขถังขยะ", "ที่อยู่ถังขยะ", "วันที่เกิดปัญหา", "สถานะ", "รายละเอียด", "วันที่แก้ไข"
        ])

        # เชื่อมต่อการคลิกที่หัวข้อคอลัมน์
        self.table.horizontalHeader().sectionClicked.connect(self.handle_header_click)

        # ปรับขนาดคอลัมน์ให้เหมาะสม
        header = self.table.horizontalHeader()
        for col in range(6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        layout.addWidget(self.table)

        # ปุ่มเพิ่มข้อความและลบรายงาน
        button_layout = QHBoxLayout()
        self.add_message_button = QPushButton("เพิ่ม/แก้ไข รายละเอียด")
        self.add_message_button.setStyleSheet("background-color: green; color: white; font-size: 14px;")

        self.add_message_button.clicked.connect(self.add_message)
        button_layout.addWidget(self.add_message_button)

        self.delete_button = QPushButton("ลบ")
        self.delete_button.setStyleSheet("background-color: red; color: white; font-size: 14px;")
        self.delete_button.clicked.connect(self.delete_report)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)
        
        # ตั้ง Layout
        self.setLayout(layout)
        self.load_report_data()

    def load_report_data(self):
        """โหลดข้อมูลจาก tbl_report ลงในตาราง"""
        reports = get_reports()
        self.update_table(reports)

    def update_table(self, reports):
        """อัปเดตข้อมูลในตาราง"""
        self.table.setRowCount(0)
        for i, report in enumerate(reports):
            self.table.insertRow(i)

            bin_location = get_bin_location(report['bin_id'])

            # เพิ่ม report_id ใน Qt.UserRole
            item = self.create_table_item(str(report['bin_id']))
            item.setData(Qt.UserRole, report.get('report_id', None))  # ใช้ get ป้องกัน KeyError
            
            self.table.setItem(i, 0, item)

            self.table.setItem(i, 1, self.create_table_item(bin_location))
            self.table.setItem(i, 2, self.create_table_item(str(report['report_date'])))
            self.table.setItem(i, 3, self.create_table_item(
                "แก้ไขแล้ว" if report['report_status'] else "ยังไม่แก้ไข"
            ))
            self.table.setItem(i, 4, self.create_table_item(report['report_message'] or "", column=4))
            self.table.setItem(i, 5, self.create_table_item(
                str(report['report_edit_date']) if report['report_edit_date'] else "None"
        ))


    def create_table_item(self, text, column=None):
        """สร้าง QTableWidgetItem พร้อมจัดกึ่งกลางและเพิ่ม tooltip"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        if column == 4:  
            item.setToolTip(text)

        return item

    def handle_header_click(self, index):
        """จัดการการคลิกหัวข้อคอลัมน์เพื่อเรียงลำดับและเพิ่มสัญลักษณ์"""
        column_name = self.table.horizontalHeaderItem(index).text().replace(" ▼", "").replace(" ▲", "")

        if column_name not in ["วันที่เกิดปัญหา", "วันที่แก้ไข"]:
            return

        # ดึงข้อมูลจากตาราง
        reports = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            report_id = item.data(Qt.UserRole)
            report_date = self.table.item(row, 2).text()
            report_edit_date = self.table.item(row, 5).text()
            reports.append({
                "report_id": report_id,
                "bin_id": self.table.item(row, 0).text(),
                "bin_location": self.table.item(row, 1).text(),
                "report_date": report_date,
                "report_status": self.table.item(row, 3).text() == "แก้ไขแล้ว",
                "report_message": self.table.item(row, 4).text(),
                "report_edit_date": report_edit_date if report_edit_date != "None" else None
            })

        # เรียงลำดับ
        reverse_order = self.sort_order[column_name]
        if column_name == "วันที่เกิดปัญหา":
            reports.sort(
                key=lambda x: datetime.strptime(x["report_date"], "%Y-%m-%d %H:%M:%S"),
                reverse=reverse_order
            )
        elif column_name == "วันที่แก้ไข":
            reports.sort(
                key=lambda x: (
                    x["report_edit_date"] is None,
                    datetime.strptime(x["report_edit_date"], "%Y-%m-%d %H:%M:%S")
                    if x["report_edit_date"] else datetime.min
                ),
                reverse=reverse_order
            )

        # สลับค่าการเรียง
        self.sort_order[column_name] = not reverse_order

        # อัปเดตตาราง
        self.update_table(reports)

        # อัปเดตหัวข้อคอลัมน์พร้อมแสดงสัญลักษณ์
        for col in range(self.table.columnCount()):
            header_text = self.table.horizontalHeaderItem(col).text().replace(" ▼", "").replace(" ▲", "")
            if header_text == column_name:
                header_text += " ▼" if reverse_order else " ▲"
            self.table.horizontalHeaderItem(col).setText(header_text)



    def apply_filters(self):
        """กรองข้อมูลตามตัวกรองที่เลือก"""
        start_date = self.date_start.date().toPyDate()
        end_date = self.date_end.date().toPyDate()
        filter_type = self.date_filter_type.currentText()
        status_filter = self.status_filter.currentText()

        reports = get_reports()  # ดึงข้อมูลทั้งหมดจากฐานข้อมูล
        filtered_reports = []

        for report in reports:
            # ตรวจสอบชนิดข้อมูลของวันที่
            report_date = report['report_date'] if filter_type == "วันที่เกิดปัญหา" else report['report_edit_date']

            # ข้ามข้อมูลที่ไม่มีวันที่ (ค่า None)
            if report_date is None:
                continue

            # หากเป็น datetime ให้แปลงเป็น date
            if isinstance(report_date, datetime):
                report_date = report_date.date()

            # ตรวจสอบช่วงวันที่
            if report_date < start_date or report_date > end_date:
                continue

            # ตรวจสอบสถานะ
            if status_filter == "แก้ไขแล้ว" and not report['report_status']:
                continue
            if status_filter == "ยังไม่แก้ไข" and report['report_status']:
                continue

            # เพิ่ม bin_location ในข้อมูลที่กรอง
            bin_location = get_bin_location(report['bin_id'])
            report['bin_location'] = bin_location
            filtered_reports.append(report)

        # อัปเดตตารางด้วยข้อมูลที่กรองแล้ว
        self.update_table(filtered_reports)

    def add_message(self):
        """เพิ่มหรือแก้ไขข้อความใน report_message"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกแถวในตาราง")
            return

        # ดึง report_id จาก Qt.UserRole
        item = self.table.item(selected_row, 0)
        report_id = item.data(Qt.UserRole)

        if not report_id:
            QMessageBox.critical(self, "Error", "ไม่พบ ID ของรายงานในแถวที่เลือก")
            return

        # แสดงหน้าต่างป้อนข้อความ
        text, ok = QInputDialog.getText(self, "Add/Update Message", "กรอกรายละเอียดข้อผิดพลาด")
        if ok and text:
            if update_report_message(report_id, text):
                QMessageBox.information(self, "Success", "อัพเดทรายละเอียดข้อผิดพลาดสำเร็จ")
                self.load_report_data()
            else:
                QMessageBox.critical(self, "Error", "ไม่สามารถอัพเดทข้อมูลได้")


    def delete_report(self):
        """ลบรายงานที่เลือก"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกแถวในตาราง")
            return

        # ดึงข้อมูลจากตาราง
        item = self.table.item(selected_row, 0)
        report_id = item.data(Qt.UserRole)
        report_date = self.table.item(selected_row, 2).text()  # ดึงวันที่เกิดปัญหา

        if not report_id:
            QMessageBox.critical(self, "Error", "ไม่พบ ID ของรายงานในแถวที่เลือก")
            return

        # ยืนยันการลบโดยแสดงวันที่เกิดปัญหา
        confirm = QMessageBox.question(
            self, "Confirm", f"คุณต้องการลบรายงานที่เกิดขึ้นวันที่ {report_date} ใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if delete_report(report_id):
                QMessageBox.information(self, "Success", f"ลบรายงานที่เกิดขึ้นวันที่ {report_date} สำเร็จ!")
                self.load_report_data()
            else:
                QMessageBox.critical(self, "Error", f"ไม่สามารถลบรายงานที่เกิดขึ้นวันที่ {report_date} ได้")
