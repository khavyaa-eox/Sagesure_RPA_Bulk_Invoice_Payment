import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from logger import listener_logger


def send_email_with_attachment_error(aname):
    subject = "Sagesure | Partial | Bulk Invoice Payment completion email"
    body = "The process had stopped due to chrome crash or unkonwn issue. Please check on priority.\n\nAttached is the partially processed file.\n\n\n************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","abhishekgs@eoxvantage.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","stefanie.lintner@sagesure.com","khavyaasridhar@eoxvantage.in"]
    # receiver_email = ["shriharim@eoxvantage.com"]
    
    password = "cpct bmuw eprv veen"
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    attachmentName = aname  # In same directory as script
    attachmentName1 = aname.replace('Output Files\\','')
    # Open PDF file in binary mode
    with open(attachmentName, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachmentName1}",
    )
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def send_email_with_attachment(aname):
    subject = "Sagesure | Bulk Invoice Payment completion email"
    body = "************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","abhishekgs@eoxvantage.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","stefanie.lintner@sagesure.com","khavyaasridhar@eoxvantage.in"]
    # receiver_email = ["shriharim@eoxvantage.com"]
    
    password = "cpct bmuw eprv veen"
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    attachmentName = aname  # In same directory as script
    attachmentName1 = aname.replace('Output Files\\','')
    # Open PDF file in binary mode
    with open(attachmentName, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachmentName1}",
    )
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def send_error_email(exp_desc):
    listener_logger.info('sending error email')
    subject = "Sagesure | Bulk Invoice Payment Error Email"
    body = f"Files could not be picked up OR \nError while accessing S3 bucket. Please check the S3 Credentials and app.log.\n Exception: {exp_desc}\n\n\n\n************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","stefanie.lintner@sagesure.com","suhass@eoxvantage.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","khavyaasridhar@eoxvantage.in"]
    password = "cpct bmuw eprv veen"
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def send_text_email(subj):
    subject = subj
    body = "Hi,\n\nPassword expired please reset and run the script again\n\n\n************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","stefanie.lintner@sagesure.com","abhishekgs@eoxvantage.com","khavyaasridhar@eoxvantage.in"]
    password = "cpct bmuw eprv veen"
    #receiver_email = ["shriharim@eoxvantage.com","abhishekgs@eoxvantage.com","pradeep@vantageagora.com"]
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def send_text_email_error(subj, filename):
    subject = subj
    body = f"The process had stopped due to chrome crash or unkonwn issue. File not processed.\n\n Filename: {filename}\n\n\n************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","stefanie.lintner@sagesure.com","abhishekgs@eoxvantage.com","khavyaasridhar@eoxvantage.in"]
    password = "cpct bmuw eprv veen"
    #receiver_email = ["shriharim@eoxvantage.com","abhishekgs@eoxvantage.com","pradeep@vantageagora.com"]
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def send_text_email_invalid(subj, exp_desc):
    subject = subj
    body = f"Hi,\n\nReceived an invalid file. Details are as below:\n{exp_desc}.\n\nPlease fix this and reshare the file\n\n\n************* Sent from Automation ************"
    sender_email = "automation@eoxvantage.com"
    receiver_email = ["kristina.tomasetti@sagesure.com","claimsvendors@sagesure.com","pradeep@vantageagora.com","shriharim@eoxvantage.com","stefanie.lintner@sagesure.com","abhishekgs@eoxvantage.com","khavyaasridhar@eoxvantage.in"]
    # receiver_email = ["shriharim@eoxvantage.com","khavyaasridhar@eoxvantage.in"]
    password = "cpct bmuw eprv veen"
    #receiver_email = ["shriharim@eoxvantage.com","abhishekgs@eoxvantage.com","pradeep@vantageagora.com"]
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = COMMASPACE.join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
        
# aname = "Output Files\\test_completed.xlsx"ASCII
# send_text_email_header("Sagesure | Column Issue","filename and missing heders")