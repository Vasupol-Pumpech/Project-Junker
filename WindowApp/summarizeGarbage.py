import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QComboBox, QCalendarWidget, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtCore import Qt
from sql import fetch_garbage_summary

class SummarizeGarbageWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Garbage Summary")
        self.setWindowIcon(QIcon("pic/sum.png"))
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        
        self.time_filter = QComboBox()
        self.time_filter.addItems(["วัน", "เดือน", "ปี", "ทั้งหมด"])
        main_layout.addWidget(self.time_filter)

        self.calendar = QCalendarWidget()
        self.calendar.setFixedHeight(300)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader) 
        main_layout.addWidget(self.calendar)
        
        self.load_button = QPushButton("โหลดข้อมูล")
        self.load_button.clicked.connect(self.update_summary)
        main_layout.addWidget(self.load_button)
        
        self.summary_boxes = {}
        summary_layout = QHBoxLayout()

        self.color_map = {
            "bottle": "#2fb6eb",
            "can": "#f94848",
            "papercup": "#e7eef9",
            "others": "#92dd7a"
        }
        
        for item, color in self.color_map.items():
            box = QWidget()
            box.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
            box_layout = QVBoxLayout()
            label = QLabel(f"{item}: 0 ชิ้น")
            label.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(label)
            box.setLayout(box_layout)
            summary_layout.addWidget(box)
            self.summary_boxes[item] = label
        
        main_layout.addLayout(summary_layout)

        self.no_data_label = QLabel("ไม่มีข้อมูลขยะในช่วงเวลานี้")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        self.no_data_label.setStyleSheet("color: red; font-size: 16px;")
        self.no_data_label.setVisible(False)
        main_layout.addWidget(self.no_data_label)
        
        self.chart_view = QChartView()
        self.chart_view.setFixedHeight(500)
        main_layout.addWidget(self.chart_view)

        self.setLayout(main_layout)

    def update_summary(self):
        selected_type = self.time_filter.currentText()
        selected_date = self.calendar.selectedDate().toString(Qt.ISODate) 

        print(f"Selected Type: {selected_type}, Selected Date: {selected_date}")

        if selected_type == "วัน":
            data = fetch_garbage_summary("day", selected_date)
        elif selected_type == "เดือน":
            data = fetch_garbage_summary("month", selected_date[:7])
        elif selected_type == "ปี":
            data = fetch_garbage_summary("year", selected_date[:4])
        else:
            data = fetch_garbage_summary("all")

        print(f"Fetched Data: {data}")

        total = sum(data.values())

        if total == 0:
            self.no_data_label.setVisible(True)
            self.chart_view.hide()
            for item in self.color_map.keys():
                self.summary_boxes[item].setText(f"{item}: 0 ชิ้น")
            return
        else:
            self.no_data_label.setVisible(False)
            self.chart_view.show()

        for item in self.color_map.keys():
            key = "non_object" if item == "others" else item
            self.summary_boxes[item].setText(f"{item}: {data.get(key, 0)} ชิ้น")

        series = QPieSeries()
        for item, count in data.items():
            key = "others" if item == "non_object" else item
            percentage = (count / total) * 100
            slice = series.append(f"{key} ({percentage:.1f}%)", count)
            slice.setBrush(QColor(self.color_map.get(key, "#000000")))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("สัดส่วนขยะ (100%)")
        chart.setMinimumSize(600, 500)
        chart.legend().setFont(QFont("Arial", 12))

        self.chart_view.setChart(chart)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SummarizeGarbageWindow()
    window.show()
    sys.exit(app.exec_())
