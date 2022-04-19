# create by andy at 2022/4/19
# reference:
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from optparse import OptionParser
from pprint import pprint

import config3
from config3 import *


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send(host, port, sender,password, receivers, subject, mesage, attachements):
    message = MIMEMultipart()
    subject = subject
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(MIMEText(mesage, 'plain', 'utf-8')),
    if attachements is not None:
        for attachement in attachements:
            att1 = MIMEText(open(attachement, 'rb').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att1["Content-Disposition"] = f'attachment; filename="{attachement}"'
            message.attach(att1)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(host=host,
                        port=port)
        smtpObj.login(user=sender,
                      password=password)
        smtpObj.sendmail(sender, receivers, message.as_string())
        logging.info("success")
    except smtplib.SMTPException as e:
        logging.info(e)
        logging.info("Error: 无法发送邮件")




def main():

    host = config.SEND_EMAIL_HOST
    port = config.SEND_EMAIL_PORT
    sender = config.SEND_EMAIL_HOST_USER
    password = config.SEND_EMAIL_HOST_PASSWORD
    receivers = [config.RECEIVE_EMAIL_HOST_USER]
    subject = "test"
    parser = OptionParser(add_help_option=True)
    parser.add_option("-H", "--host", dest="host", default=host, type="str",
                      help="host of the sender")
    parser.add_option("-P", "--port", dest="port", default=port, type="int",
                      help="port of the sender")
    parser.add_option("-s", "--sender", dest="sender", default=sender, type="str",
                      help="who send the email")
    parser.add_option("-p", "--password", dest="password", default=password, type="str",
                      help="the password to the server")
    parser.add_option("-r", "--receivers", dest="receivers", default=receivers, type="str",
                      action="append",
                      help="who will reveive the email")
    parser.add_option("-S", "--subject", dest="subject", default=subject, type="str",
                      help="the subject of the email")
    parser.add_option("-m", "--message", dest="message", type="str",
                      help="the context of the email")
    parser.add_option("-a", "--attachments", dest="attachments", type="str",
                      action="append",
                      help="attachments")

    (options, args) = parser.parse_args()
    send(host=options.host,
         port=options.port,
         sender=options.sender,
         password=options.password,
         receivers=options.receivers,
         subject=options.subject,
         mesage=options.message,
         attachements=options.attachments)

if __name__ == '__main__':
    main()
