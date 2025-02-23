from PyQt5.QtWidgets import (QComboBox, QDialog,QLabel, QLineEdit,QMessageBox,QPushButton, QVBoxLayout)
from sql import get_bin_location, update_bin_location, delete_bin,get_bin

class DeletePopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ลบถังขยะ")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Dropdown สำหรับเลือก Bin ID
        bin_id_label = QLabel("เลือก Bin ID:")
        layout.addWidget(bin_id_label)

        self.bin_id_dropdown = QComboBox()
        bin_data = get_bin()  # ดึงข้อมูล Bin ID ทั้งหมด
        for bin_row in bin_data:
            display_text = f"Bin ID: {bin_row['bin_id']} - อยู่ที่: {bin_row['bin_location']}"
            self.bin_id_dropdown.addItem(display_text, bin_row["bin_id"])
        layout.addWidget(self.bin_id_dropdown)

        # ปุ่ม Delete
        delete_button = QPushButton("ลบ")
        delete_button.setStyleSheet("background-color: red; color: white;")
        delete_button.clicked.connect(self.delete_bin)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def delete_bin(self):
        """ลบข้อมูลถังขยะ"""
        selected_bin_id = self.bin_id_dropdown.currentData()

        # เช็คจำนวนถังขยะในฐานข้อมูล
        bin_data = get_bin()
        if len(bin_data) <= 1:
            QMessageBox.warning(
                self, "Operation Not Allowed", "ไม่สามารถลบได้ เนื่องจากเหลือถังขยะเพียงรายการเดียวในระบบ"
            )
            return

        # ยืนยันการลบ
        reply = QMessageBox.question(
            self, "Confirm Delete", f"คุณต้องการลบ Bin ID {selected_bin_id} หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if delete_bin(selected_bin_id):
                QMessageBox.information(self, "Success", f"ลบ Bin ID {selected_bin_id} เรียบร้อยแล้ว")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "ไม่สามารถลบข้อมูลได้")




class EditPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("แก้ไขถังขยะ")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Dropdown สำหรับเลือก Bin ID
        bin_id_label = QLabel("เลือก Bin ID:")
        layout.addWidget(bin_id_label)

        self.bin_id_dropdown = QComboBox()
        bin_data = get_bin()  # ดึงข้อมูล Bin ID ทั้งหมด
        for bin_row in bin_data:
            self.bin_id_dropdown.addItem(f"Bin ID: {bin_row['bin_id']}", bin_row["bin_id"])
        self.bin_id_dropdown.currentIndexChanged.connect(self.update_location_field)
        layout.addWidget(self.bin_id_dropdown)

        # Textbox สำหรับแก้ไข Location
        location_label = QLabel("Location:")
        layout.addWidget(location_label)

        self.location_input = QLineEdit()
        layout.addWidget(self.location_input)

        # ปุ่ม Save
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_to_database)
        layout.addWidget(save_button)

        self.setLayout(layout)

        # ตั้งค่า Location เริ่มต้น
        self.update_location_field()

    def update_location_field(self):
        """อัปเดตฟิลด์ Location เมื่อเลือก Bin ID ใหม่"""
        selected_bin_id = self.bin_id_dropdown.currentData()
        current_location = get_bin_location(selected_bin_id)
        self.location_input.setText(current_location)

    def save_to_database(self):
        """บันทึกข้อมูลที่แก้ไขไปยังฐานข้อมูล"""
        selected_bin_id = self.bin_id_dropdown.currentData()
        new_location = self.location_input.text().strip()

        if not new_location:
            QMessageBox.warning(self, "Warning", "กรุณากรอก Location ก่อนบันทึก")
            return

        if update_bin_location(selected_bin_id, new_location):
            QMessageBox.information(self, "Success", "บันทึกข้อมูลเรียบร้อยแล้ว")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "ไม่สามารถบันทึกข้อมูลได้")
