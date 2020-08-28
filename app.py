import os
import random
import time
import pickle
from threading import Thread, Lock

from flask import Flask, render_template, json, request
from email_api import send_solution


from solver import Solver

# define application
app = Flask(__name__)

# TODO: remove unused api keys throughout the file
def api_key_generator():
    """
    Generate unique api keys.
    There are 536,236,100,573,742,000,000 possible keys.
    """

    while True:
        key = ""
        for _ in range(12):
            choices = (random.randint(48, 57), random.randint(65, 90), random.randint(97, 122))
            key += chr(random.choice(choices))
        if not (key in used_keys):
            used_keys.add(key)
            yield key

used_keys = set()
api_keys = api_key_generator()

job_lock = Lock() # create a lock on the jobs
jobs = [] # api key to input file
processing = False # whether the server is currently processing a job

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
                file_name f"./solutions/solution_{num}"
                num += 1
            solver.save_result(file_name)
            send_solution(email, file_name)
            processing = False
            time.sleep(1)
        
        with job_lock:
            for job in job_queue:
                jobs.remove(job)

server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()

def prepare_file(f):
    # TODO: prepare the file for the solver
    return f

def is_safe(f):
    # TODO: write antivirus
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

            # TODO: send them a confirmation email

            return "Upload successful!"

    # all else fails, return to home
    return "Upload failed!"

@app.route("/get_new_key", methods=["GET"])
def get_new_key():
    return next(api_keys)

@app.route("/result/<key>")
def get_result(key=""):
    solutions = os.listdir("solutions")
    for solution_file in solutions:
        if solution_file.endswith(key):
            break
    else:
        return render_template("still_processing.html")
    
    # TODO: send file back
