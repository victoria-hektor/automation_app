from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.models import Report, Task
from datetime import datetime
import os

@app.route('/')
@app.route('/index')
def index():
    reports = Report.query.all()
    return render_template('index.html', reports=reports)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        email = request.form['email']
        schedule_time = request.form['schedule_time']
        task = Task(email=email, schedule_time=datetime.strptime(schedule_time, '%Y-%m-%dT%H:%M'))
        db.session.add(task)
        db.session.commit()
        flash('Report scheduled successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('schedule.html')

@app.route('/download/<int:report_id>')
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    return redirect(url_for('static', filename=report.file_path))