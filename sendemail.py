import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "7xaverix7@gmail.com"
receiver_email = "kimkevin2657@naver.com"
password = "RLAqudcjf7928!"

message = MIMEMultipart("alternative")
message["Subject"] = "터치콘 이메일 인증코드"
message["From"] = sender_email
message["To"] = receiver_email

verificationcode = 521

# Create the plain-text and HTML version of your message
text = """\
{}
""".format(verificationcode)

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")

message.attach(part1)


# Create secure connection with server and send email
context = ssl.create_default_context()


server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
server.login(sender_email, password)
server.sendmail(
    sender_email, receiver_email, message.as_string()
)

"""
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )

"""


