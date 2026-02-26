class Task:
    def __init__(self, title, category, due_date):
        self.title = title
        self.category = category
        self.due_date = due_date
        self.is_completed = False
        self.is_archived = False 

    def archive(self):
        self.is_archived = True
        
    def toggle_complete(self):
        self.is_completed = not self.is_completed

    def mark_complete(self):
        self.is_completed = True

    def __str__(self):
        status = "✅" if self.is_completed else "⏳"
        return f"{status} {self.title} ({self.category}) - Due: {self.due_date}"
    
class Scheduler:
    def __init__(self, owner_name):
        self.owner = owner_name
        self.tasks = []

    def add_task(self, title, category, due_date):
        new_task = Task(title, category, due_date)
        self.tasks.append(new_task)

    def show_all_tasks(self):
        print(f"--- {self.owner}'s Schedule ---")
        for t in self.tasks:
            print(t)