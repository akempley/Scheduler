import os
import sys
import sqlite3
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QLineEdit)
from PySide6.QtCore import Qt, QPoint, QTimer

# This handles the path whether you're running in VSCode or as a built .app
if getattr(sys, 'frozen', False):
    # If the app is "frozen" (bundled), find the folder the .app is in
    base_path = os.path.dirname(sys.executable)
else:
    # If running normally in VSCode
    base_path = os.path.dirname(os.path.abspath(__file__))

db_path = '/Applications/Productivity Tool/scheduler.db'

class SoloSchedulerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()
        self.init_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull():
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Applying the Neon Styles
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #00ffcc; border: 2px solid #333; border-radius: 15px; font-family: 'Avenir', sans-serif; }
            QLabel#title { font-weight: bold; font-size: 16px; color: #ffffff; padding: 5px; border: none; }
            QLineEdit { background-color: #1a1a1a; border: 1px solid #00ffcc; border-radius: 5px; padding: 5px; color: white; margin: 5px; }
            QListWidget { background-color: #1a1a1a; border: 1px solid #444; border-radius: 8px; margin: 5px; }
            QPushButton { background-color: #222; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 8px; padding: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #00ffcc; color: #121212; }
            QPushButton#close { border-color: #ff5555; color: #ff5555; }
        """)

        layout = QVBoxLayout()
        
        self.title = QLabel("Solo Scheduler")
        self.title.setObjectName("title")
        layout.addWidget(self.title)

        # ADD TASK SECTION
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        self.task_input.returnPressed.connect(self.add_task_to_db) # Add on 'Enter' key
        layout.addWidget(self.task_input)

        self.add_btn = QPushButton("Add Task")
        self.add_btn.clicked.connect(self.add_task_to_db)
        layout.addWidget(self.add_btn)

        # TASK LIST
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        # BOTTOM BUTTONS
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_tasks)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("close")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setFixedSize(280, 450)
        self.load_tasks()

    def add_task_to_db(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return

        try:
            # Removed the local db_path line so it uses the one at the top of the file
            conn = sqlite3.connect(db_path) 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO task (title, category, is_completed) VALUES (?, ?, ?)", 
                           (task_text, 'Desktop', 0))
            conn.commit()
            conn.close()
            self.task_input.clear()
            self.load_tasks()
        except sqlite3.Error as e:
            self.task_list.addItem(f"Add Error: {e}")

    def load_tasks(self):
        try:
            # Removed the local db_path line here too
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM task WHERE is_completed = 0")
            rows = cursor.fetchall()
            self.task_list.clear()
            for row in rows:
                self.task_list.addItem(f"• {row[0]}")
            conn.close()
        except sqlite3.Error as e:
            self.task_list.addItem(f"Load Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoloSchedulerWidget()
    window.show()
    sys.exit(app.exec())