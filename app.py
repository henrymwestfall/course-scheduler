import os
import random
import time
import pickle
from threading import Thread, Lock
from smtplib import SMTP, SMTPAuthenticationError

from flask import Flask, render_template, json, request
from email_api import send_solution, send_plaintext_email


from solver import Solver

# define application
app = Flask(__name__)

job_lock = Lock() # create a lock on the jobs
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
            with open(file_name, "r") as f:
                data = prepare_file(f)

            solver = Solver()
            solver.load_problem(data)
            solver.solve()

            filename = "./solutions/solution_0"
            num = 1
            while os.path.exists(file_name):
                file_name = f"./solutions/solution_{num}"
                num += 1
            solver.save_result(file_name)
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
        except SMPTAuthenticationError:
            print("Invalid password. Please try again.")
    else:
        print("You have reached the maximum number of login attempts. Try again in 10 minutes")
        time.sleep(600)

server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()


def prepare_file(f):
    # TODO: prepare the file for the solver
    return f

def is_safe(f):
    # TODO: check the file for security risks
    return True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        email = request.files["email"]
        if is_safe(f):
            ext = f.filename.split(".")[1]
            name = "/input_files/input_file_0.csv"
            num = 1
            while os.path.exists(name):
                name = f"/input_files/input_file_{num}.csv"
                num += 1
            f.save(name)

            with job_lock:
                jobs.append((email, name))

            send_plaintext_email(email, sender_pass, "Hello,\nYour schedule request has been received. We will email you when the solution is ready.")

            return "Upload successful!"

    return "Upload failed!"

@app.route("/get_new_key", methods=["GET"])
def get_new_key():
    return next(api_keys)