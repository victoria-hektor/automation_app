from app import db
from app.models import Task, Report
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

scheduler = BackgroundScheduler()

def generate_report(task):
    # Example: Generate a simple report
    data = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2020', periods=10),
        'Sales': [x*10 for x in range(10)]
    })

    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'], data['Sales'])
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.title('Sales Over Time')
    file_path = f"reports/report_{task.id}.png"
    plt.savefig(file_path)
    
    # Create PDF
    pdf_path = f"reports/report_{task.id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Automated Report")
    c.drawString(100, 730, f"Generated on: {datetime.utcnow()}")
    c.drawImage(file_path, 100, 500, width=400, height=300)
    c.save()

    report = Report(name=f"Report {task.id}", file_path=pdf_path)
    db.session.add(report)
    db.session.commit()
    
    send_email(task.email, pdf_path)

def send_email(to_email, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = to_email
    msg['Subject'] = "Your Automated Report"

    body = "Please find the attached report."
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(attachment_path, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
    msg.attach(p)

    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(msg['From'], 'your_password')
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

def schedule_task(task_id):
    task = Task.query.get(task_id)
    trigger = DateTrigger(run_date=task.schedule_time)
    scheduler.add_job(generate_report, trigger, args=[task])
    scheduler.start()

# Schedule all tasks in the database
tasks = Task.query.all()
for task in tasks:
    schedule_task(task.id)