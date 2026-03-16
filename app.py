import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from models import Task
from datetime import date
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Same scope as the widget
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Applications/Productivity Tool/scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def sync_to_google(task_title, due_date):
    creds = None
    # Pointing to your centralized folder
    base_folder = '/Applications/Productivity Tool/'
    token_path = os.path.join(base_folder, 'token.json')
    creds_path = os.path.join(base_folder, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Note: This will open a browser tab on your Mac server
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': task_title,
            'description': 'Added via Flask Web Interface',
            'start': {'date': due_date},
            'end': {'date': due_date},
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return True
    except Exception as e:
        print(f"Flask Google Sync Error: {e}")
        return False

#still keeping my old work
"""my_scheduler = Scheduler("AAron")

# Testing
my_scheduler.add_task("IT111 Lab 5", "School", "2026-03-01")
my_scheduler.add_task("Bartending Shift", "Work", "2026-02-28")"""

@app.route('/')
def show_scheduler():
    today = date.today().strftime('%Y-%m-%d')
    tasks = Task.query.all()
    return render_template('scheduler.html', tasks=tasks, today=today)
    # We only send tasks that are NOT archived OR haven't expired yet
    """return render_template('scheduler.html', 
                           tasks=my_scheduler.tasks, 
                           today=today)"""

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    category = request.form.get('category')
    due_date = request.form.get('due_date')

    # 1. Save to Database
    new_task = Task(title=title, category=category, due_date=due_date)
    db.session.add(new_task)
    db.session.commit()

    # 2. Sync to Google Calendar
    sync_to_google(title, due_date)

    return redirect(url_for('show_scheduler'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.toggle_complete()
    db.session.commit()
    
    return redirect(url_for('show_scheduler'))
    # 1. Safety check to make sure the index is valid
    """if 0 <= index < len(my_scheduler.tasks):
        # 2. Call the toggle method we built in models.py
        my_scheduler.tasks[index].toggle_complete()
        
    # 3. Bounce back to the home page to see the neon checkmark
    return redirect(url_for('show_scheduler'))"""

@app.route('/archive/<int:task_id>')
def archive_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.archive()
    db.session.commit()
    
    return redirect(url_for('show_scheduler'))
    """if 0 <= index < len(my_scheduler.tasks):
        # We call the archive method instead of deleting
        my_scheduler.tasks[index].archive()
    return redirect(url_for('show_scheduler'))"""

if __name__ == '__main__':
    # debug=True lets you see errors in the browser—great for schoolwork! a.i. helped me with this part
    app.run(debug=True)


