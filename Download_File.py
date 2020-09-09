import pyrebase


def download():
    config = {
        "apiKey": "AIzaSyDgKVxrtI1vGEwCrxulpv6IS5Cum3bgE3k",
        "authDomain": "course-scheduler-7510d.firebaseapp.com",
        "databaseURL": "https://course-scheduler-7510d.firebaseio.com",
        "projectId": "course-scheduler-7510d",
        "storageBucket": "course-scheduler-7510d.appspot.com",
        "messagingSenderId": "537642069863",
        "appId": "1:537642069863:web:f231b8526fc40b335ec9c2",
        "measurementId": "G-FCWEEZNR0T",
        
        
    }

    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    file_in_database = "Requests.csv"
    local_file = "Requests.csv"
    storage.child(file_in_database).download(local_file)
    file_in_database = "Teacher Qualifications.csv"
    local_file = "Teacher Qualifications.csv"
    storage.child(file_in_database).download(local_file)
