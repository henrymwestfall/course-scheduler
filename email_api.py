import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_plaintext_email(receiver_address, text):
    sender_address = 'coursescheduler640@gmail.com'
    sender_pass = 'NCEu9ZxyVH6WByP'

    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

def send_solution(receiver_address, attach_file_name):
    sender_address = 'coursescheduler640@gmail.com'
    sender_pass = 'NCEu9ZxyVH6WByP'

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = "Your Schedules Are Ready!"
    mail_content = '''Hello,
    Your schedules are ready! Download the attached CSV file.
    '''

    message.attach(MIMEText(mail_content, 'plain'))
    payload = MIMEBase('application', 'octate-stream')
    with open(attach_file_name, 'rb') as attach_file: # Open the file as binary mode 
        payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) #encode the attachment
    payload.add_header('Content-Disposition', 'attachment', filename="Schedules")
    message.attach(payload)

    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()