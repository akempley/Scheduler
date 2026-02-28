import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
from extensions import db
from models import Task

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scheduler.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


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

    new_task = Task(title=title, category=category, due_date=due_date)

    #my_scheduler.add_task(title, category, due_date)
    db.session.add(new_task)
    db.session.commit()

    # THIS IS THE KEY: Send the user back to the home route
    # 'show_scheduler' is the name of your function for the '/' route
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


