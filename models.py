from extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)

    def archive(self):
        self.is_archived = True

    def toggle_complete(self):
        self.is_completed = not self.is_completed

    def mark_complete(self):
        self.is_completed = True

    def __str__(self):
        status = "✅" if self.is_completed else "⏳"
        return f"{status} {self.title} ({self.category}) - Due: {self.due_date}"
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
#keeping this so I don't forget my work moving into sql    
"""class Scheduler:
    def __init__(self, owner_name):
        self.owner = owner_name
        self.tasks = []

    def add_task(self, title, category, due_date):
        new_task = Task(title, category, due_date)
        self.tasks.append(new_task)

    def show_all_tasks(self):
        print(f"--- {self.owner}'s Schedule ---")
        for t in self.tasks:
            print(t)"""