import os
import random
import time
from threading import Thread, Lock

from flask import Flask, render_template, json, request

from solver import Solver

# define application
app = Flask(__name__)

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
jobs = {} # api key to input file
finished = {} # list of api keys with finished jobs
processing = False # whether the server is currently processing a job

def server():
    """
    Infinitely check for jobs. When jobs are found, process and solve them.
    """

    while True:
        with job_lock:
            job_queue = jobs.copy()

        for key, file_name in job_queue.items():
            with open(file_name, "r") as f:
                data = prepare_file(f)

            solver = Solver()
            solver.load_problem(data)
            solver.solve()
            solver.save_result(f"solution_{key}") # TODO: save the result to a file

            time.sleep(1)
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

@app.route("/upload/<key>", methods=["POST"])
def upload(key=""):
    if not (key in used_keys):
        return "Unknown key"
    elif key in jobs:
        return "Key is in use."

    if request.method == "POST":
        f = request.files["input_file"]
        if is_safe(f):
            ext = f.filename.split(".")[1]
            name = f"/input_files/input_file_{key}.{ext}"
            f.save(name)

            with job_lock:
                jobs[key] = name

            return render_template("upload_success.html")

    # all else fails, return to home
    return render_template("index.html")

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
