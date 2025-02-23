from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, QInputDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from sql import get_bin, update_bin_location, delete_bin

class TrashDetailWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Trash Details")
        self.setFixedSize(1000, 600)
        self.setWindowIcon(QIcon("pic/detail.png"))
        # Layout หลัก
        layout = QVBoxLayout()

        # ตารางแสดงข้อมูล
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["หมายเลขถังขยะ", "ที่อยู่ถังขยะ", "สถานะถังขยะ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        layout.addWidget(self.table)

        # ปุ่ม
        button_layout = QHBoxLayout()

        self.edit_button = QPushButton("แก้ไขที่อยู่ถังขยะ")
        self.edit_button.clicked.connect(self.edit_bin_location)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("ลบถังขยะ")
        self.delete_button.clicked.connect(self.delete_bin)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # โหลดข้อมูลจากฐานข้อมูล
        self.load_bin_data()

    def load_bin_data(self):
        """โหลดข้อมูลถังขยะจากฐานข้อมูล"""
        bins = get_bin()
        self.table.setRowCount(0)
        for i, bin_data in enumerate(bins):
            self.table.insertRow(i)
            self.table.setItem(i, 0, self.create_table_item(str(bin_data['bin_id'])))
            self.table.setItem(i, 1, self.create_table_item(bin_data['bin_location'], column=1))
            status_text = "กำลังทำงาน" if bin_data['bin_status'] == 1 else "ขาดการเชื่อมต่อ"
            self.table.setItem(i, 2, self.create_table_item(status_text))

    def create_table_item(self, text,column=None):
        """สร้าง QTableWidgetItem พร้อมจัดกึ่งกลาง"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        if column == 1:  
            item.setToolTip(text)
        return item

    def edit_bin_location(self):
        """แก้ไขที่อยู่ถังขยะ"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกแถวในตาราง")
            return

        bin_id = int(self.table.item(selected_row, 0).text())
        current_location = self.table.item(selected_row, 1).text()

        # แสดงหน้าต่างป้อนข้อมูลใหม่
        new_location, ok = QInputDialog.getText(self, "แก้ไขที่อยู่ถังขยะ", "ที่อยู่ใหม่:", text=current_location)
        if ok and new_location:
            if update_bin_location(bin_id, new_location):
                QMessageBox.information(self, "Success", "แก้ไขที่อยู่ถังขยะสำเร็จ")
                self.load_bin_data()
            else:
                QMessageBox.critical(self, "Error", "ไม่สามารถแก้ไขที่อยู่ถังขยะได้")

    def delete_bin(self):
        """ลบถังขยะ"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกแถวในตาราง")
            return

        bin_id = int(self.table.item(selected_row, 0).text())
        bin_location = self.table.item(selected_row, 1).text()

        # ยืนยันการลบ
        confirm = QMessageBox.question(
            self, "Confirm", f"คุณต้องการลบถังขยะที่ {bin_location} ใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if delete_bin(bin_id):
                QMessageBox.information(self, "Success", f"ลบถังขยะที่ {bin_location} สำเร็จ!")
                self.load_bin_data()
            else:
                QMessageBox.critical(self, "Error", f"ไม่สามารถลบถังขยะที่ {bin_location} ได้")
