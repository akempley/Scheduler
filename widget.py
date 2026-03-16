import os
import sys
import sqlite3
import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QLineEdit, QDateEdit, QListWidgetItem)
from PySide6.QtCore import Qt, QPoint, QTimer, QDate
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- PYINSTALLER PATH FIX ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Updated to use the resource_path helper
db_path = resource_path('scheduler.db')
creds_path = resource_path('credentials.json')
token_path = resource_path('token.json')

def sync_to_google(task_title, due_date):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': task_title,
            'description': 'Added via Solo Scheduler Widget',
            'start': {'date': due_date},
            'end': {'date': due_date},
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return True
    except Exception as e:
        print(f"Google Sync Error: {e}")
        return False

class SoloSchedulerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
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

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        self.task_input.returnPressed.connect(self.add_task_to_db)
        layout.addWidget(self.task_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate()) 
        self.date_input.setStyleSheet("color: white; background-color: #1a1a1a; padding: 5px;")
        layout.addWidget(self.date_input)

        self.add_btn = QPushButton("Add Task")
        self.add_btn.clicked.connect(self.add_task_to_db)
        layout.addWidget(self.add_btn)

        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.archive_task)
        layout.addWidget(self.task_list)

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
        self.setFixedSize(280, 480)
        self.load_tasks()

    def add_task_to_db(self):
        task_text = self.task_input.text().strip()
        picked_date = self.date_input.date().toString("yyyy-MM-dd")
        if not task_text: 
            return

        try:
            conn = sqlite3.connect(db_path, timeout=10) 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO task (title, category, is_completed, due_date) VALUES (?, ?, ?, ?)", 
                           (task_text, 'Desktop', 0, picked_date))
            conn.commit()
            conn.close()

            self.task_input.clear()
            self.load_tasks() 

            sync_success = sync_to_google(task_text, picked_date)
            
            if not sync_success:
                self.title.setText("Saved Locally (Sync Failed)")
            else:
                self.title.setText("Synced to Google!")
            
            QTimer.singleShot(3000, lambda: self.title.setText("Solo Scheduler"))

        except sqlite3.Error as e:
            self.title.setText("DB Error!")
            print(f"Database Error: {e}")
            
    def archive_task(self, item):
        task_id = item.data(Qt.UserRole)
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("UPDATE task SET is_completed = 1 WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            self.load_tasks()
        except sqlite3.Error as e:
            self.task_list.addItem(f"Archive Error: {e}")

    def load_tasks(self):
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM task WHERE is_completed = 0")
            rows = cursor.fetchall()
            self.task_list.clear()
            for row in rows:
                item = QListWidgetItem(f"• {row[1]}")
                item.setData(Qt.UserRole, row[0])
                self.task_list.addItem(item)
            conn.close()
        except sqlite3.Error as e:
            self.task_list.addItem(f"Load Error: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull():
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoloSchedulerWidget()
    window.show()
    sys.exit(app.exec())