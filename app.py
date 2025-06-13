from flask import Flask, render_template, request, redirect, session
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        faculty_name = request.form['faculty_name']
        session['faculty_name'] = faculty_name.strip().lower()
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    faculty_name = session.get('faculty_name')
    if not faculty_name:
        return redirect('/login')

    df = pd.read_csv('timetable.csv')
    df['faculty_name'] = df['faculty_name'].str.strip().str.lower()

    # Filter based on logged-in faculty
    faculty_df = df[df['faculty_name'] == faculty_name]

    # For current/next/previous lecture logic
    def get_status(row):
        try:
            start = datetime.strptime(row['start_time'], "%H:%M").time()
            end = datetime.strptime(row['end_time'], "%H:%M").time()
        except:
            return 'past'
        now = datetime.now().time()
        if start <= now <= end:
            return 'current'
        elif now < start:
            return 'upcoming'
        else:
            return 'past'

    faculty_df['status'] = faculty_df.apply(get_status, axis=1)
    lectures = faculty_df.to_dict(orient='records')

    # Build timetable structure
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = sorted(df['start_time'].unique())

    timetable = {}
    for _, row in faculty_df.iterrows():
        key = (row['day'], row['start_time'])
        timetable[key] = {
            'subject': row['subject'],
            'classroom': row['classroom']
        }

    return render_template(
        'dashboard.html',
        faculty=faculty_name,
        lectures=lectures,
        days=days,
        time_slots=time_slots,
        timetable=timetable
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
