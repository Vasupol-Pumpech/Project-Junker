from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import webbrowser

class AboutUsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("เกี่ยวกับเรา")
        self.setFixedSize(500, 200)  # ปรับขนาดหน้าต่างให้กระชับขึ้น
        self.setWindowIcon(QIcon("pic/info.png"))  

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10) 
        layout.setSpacing(5) 

        # รายชื่อทีมงาน
        team = [
            {"name": "นายวสุพล ปุ่มเพ็ชร", "id": "116410462003-7", "email": "vasupol.pu@gmail.com", "phone": "0995534257", "image": "pic/vasupol.png"},
            {"name": "นายดำรงรัตน์  ปีมณี", "id": "116410462005-2", "email": "gg505890@gmail.com", "phone": "0614310916", "image": "pic/damloung.png"},
            {"name": "นายณัฐชนน  เปียนขุนทด", "id": "116410400569-2", "email": "preeya@example.com", "phone": "0934567890", "image": "pic/nutchanon.png"}
        ]

        # วางแนวนอน 3 คน
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)  

        for member in team:
            member_layout = QVBoxLayout()
            member_layout.setSpacing(1) 

            # รูปภาพ
            pixmap = QPixmap(member["image"])
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(80, 100, Qt.KeepAspectRatio))  # ปรับขนาดภาพให้เล็กลง
            image_label.setAlignment(Qt.AlignCenter)
            member_layout.addWidget(image_label)

            # ชื่อ + รหัสนักศึกษา
            name_label = QLabel(f"<b>{member['name']}</b><br>รหัส: {member['id']}")
            name_label.setAlignment(Qt.AlignCenter)
            member_layout.addWidget(name_label)

            # อีเมล (mailto)
            email_button = QPushButton(member["email"])
            email_button.setStyleSheet("font-size: 10px; padding: 3px;")  # ปรับขนาดปุ่ม
            email_button.clicked.connect(lambda checked, email=member["email"]: webbrowser.open(f"mailto:{email}"))
            member_layout.addWidget(email_button)

            # เบอร์โทร (tel)
            phone_button = QPushButton(member["phone"])
            phone_button.setStyleSheet("font-size: 10px; padding: 3px;")  # ปรับขนาดปุ่ม
            phone_button.clicked.connect(lambda checked, phone=member["phone"]: webbrowser.open(f"tel:{phone}"))
            member_layout.addWidget(phone_button)

            row_layout.addLayout(member_layout)

        layout.addLayout(row_layout)
        self.setLayout(layout)