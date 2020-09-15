import os
import random
import time
import pickle
from zipfile import ZipFile
from threading import Thread, Lock
from smtplib import SMTP, SMTPAuthenticationError

from flask import Flask, render_template, json, request
from email_api import send_solution, send_plaintext_email


from solver import Solver

# define application
app = Flask(__name__)

job_lock = Lock() # create a lock on the jobs
tempfile_lock = Lock() # create a lock on temporary files
jobs = [] # list of (email, filename) pairs

def server():
    """
    Infinitely check for jobs. When jobs are found, process and solve them.
    """

    while True:
        with job_lock:
            job_queue = jobs.copy()

        for email, file_name in job_queue:
            processing = True

            with tempfile_lock:
                zf_obj = ZipFile(file_name)
                solver = Solver(zf_obj)
            solver.solve()

            filename = "./solutions/solution_0"
            num = 1
            while os.path.exists(file_name):
                file_name = f"./solutions/solution_{num}"
                num += 1
            solver.save(file_name)
            send_solution(email, sender_pass, file_name)
            processing = False
            time.sleep(1)
        
        with job_lock:
            for job in job_queue:
                jobs.remove(job)

# login
sender_pass = ""
valid = False
while not valid:
    for i in range(5):
        sender_pass = input("Enter the password for coursescheduler640@gmail.com: ")
        session = SMTP('smtp.gmail.com', 587)
        session.starttls()
        try:
            session.login("coursescheduler640@gmail.com", sender_pass)
            valid = True
            break
        except SMTPAuthenticationError:
            print("Invalid password. Please try again.")
    else:
        print("You have reached the maximum number of login attempts. Try again after 10 minutes")
        time.sleep(600)

server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()

def is_safe(f):
    # TODO: check the file for security risks
    return True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        student_requests_file = request.files["student-requests"]
        teacher_qualifs_file = request.files["teacher-qualifs"]
        email = request.form["email"]
        if is_safe(student_requests_file) and is_safe(teacher_qualifs_file):
            name = "input_files/input_file_0.zip"
            num = 1
            while os.path.exists(name):
                name = f"input_files/input_file_{num}.zip"
                num += 1
            
            # create zip files from temporary files
            with tempfile_lock:
                with open("temporary_files/requests.csv", "wb") as trf:
                    trf.write(student_requests_file.read())
                with open("temporary_files/qualifications.csv", "wb") as tqf:
                    tqf.write(teacher_qualifs_file.read())
                with ZipFile(name, "w") as zf:
                    zf.write("temporary_files/requests.csv")
                    zf.write("temporary_files/qualifications.csv")

            with job_lock:
                jobs.append((email, name))

            text = f"""Subject: Upload Success\n
            Hello,

            Your schedule request has been received. We will send you another email when the solution is ready.
            """
            send_plaintext_email(email, sender_pass, text)

            return "Upload successful!"

    return "Upload failed!"

@app.route("/get_new_key", methods=["GET"])
def get_new_key():
    return next(api_keys)