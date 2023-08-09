import os

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
db = SQLAlchemy(app)

# Database models
class DJPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    preferences = db.Column(db.String(120), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule = db.Column(db.String(300), nullable=False)

# List of DJs
DJS = ["Mark Redito", "Unagi", "Surelawn", "Swooky", "4eyes"]

def generate_corrected_schedule_with_times(preferences):
    flattened_preferences = [(dj, rank, time) for dj, times in preferences.items() for rank, time in enumerate(times)]
    sorted_preferences = sorted(flattened_preferences, key=lambda x: (x[1], x[2]))
    
    # Set times based on the order
    set_times = ["2:30 pm", "3:30 pm", "4:30 pm", "5:30 pm", "6:30 pm"]
    
    # Ensuring each DJ is assigned only once
    assigned_djs = set()
    assigned_times = []
    time_idx = 0
    for x in sorted_preferences:
        if x[0] not in assigned_djs:
            assigned_times.append(f"{x[0]} ({set_times[time_idx]})")
            assigned_djs.add(x[0])
            time_idx += 1
    return [assigned_times]

# Main Flask route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        preferences = ",".join([request.form['pref1'], request.form['pref2'], request.form['pref3'], request.form['pref4'], request.form['pref5']])
        new_preference = DJPreference(name=name, preferences=preferences)
        db.session.add(new_preference)
        db.session.commit()

        # Check if all DJs have input their preferences
        dj_preferences = {dj.name for dj in DJPreference.query.all()}
        if set(DJS) == dj_preferences:
            all_preferences = {dj.name: [int(p) for p in dj.preferences.split(',')] for dj in DJPreference.query.all()}
            schedule = generate_corrected_schedule_with_times(all_preferences)[0]  # Get the single generated schedule

            # Clear out any existing schedules in the database
            Schedule.query.delete()

            # Add the new schedule to the database
            new_schedule = Schedule(schedule=','.join(schedule))
            db.session.add(new_schedule)
            db.session.commit()

        return redirect(url_for('index'))
    
    preferences = DJPreference.query.all()
    schedules = Schedule.query.all()
    return render_template('index.html', preferences=preferences, schedules=schedules)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
