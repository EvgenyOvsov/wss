# Evgeny Ovsov

'''
Sending e-mails via SMTP.
Letters can contain plain text only, or text + html-version.
'''

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import sys

import config


class MailAgent:
    '''
    Agent for sending emails
    All calls must be made like MailAgent.get().somefuction()

    (This reduces the time of sending letters, allowing you to connect to the smtp server only once and keep the connection)
    '''

    _instance = None

    @staticmethod
    def get():
        '''
        :return: configured MailAgent
        '''
        if MailAgent._instance is None:
            MailAgent._instance = MailAgent()
        return MailAgent._instance

    def __init__(self):
        try:
            self.__agent = smtplib.SMTP_SSL(config.SMTP['provider'], 465, context=ssl.create_default_context())
            self.__agent.login(user=config.SMTP['login'],
                               password=config.SMTP['password'])
        except smtplib.SMTPAuthenticationError as e:
            print(f"Something wrong with SMTP-mailagent.\n{e}", file=sys.stderr)

    def __del__(self):
        try:
            self.__agent.quit()
        except smtplib.SMTPServerDisconnected:
            pass

    def __str__(self):
        return str(config.SMTP) # When print directly object of class - print info about connection

    def send_mail(self, letter_type, to_addrs: str, code=None, name='madam/sir'):
        '''
        Send mail to the client
        :param letter_type: template
        :param to_addrs: client's e-mail
        :param code: randomly generated code
        :param name: name of client
        :return: None
        '''
        def get_code_mail(code):
            message = MIMEMultipart('alternative')
            message['subject'] = "Link"
            message['From'] = config.SMTP["login"]
            message['To'] = to_addrs
            text = f'Hello, dear {name}\nSomeone, maybe you, requested autorization code...\n' \
                f'If it was not you, just ignore that letter, but... If it was you...\nHere is the code:{code}'
            html = f'''
            <html>
            <head></head>
            <body>
            <h3>Someone, maybe you, requested autorization code...</h3><br><br><br>
            <img src="https://upload.wikimedia.org/wikipedia/ru/2/2a/Nashville_desktop.jpg"></img>
            <p>Hello, dear {name}!</p>
            <p>Someone requested the code. If it was not you, just ignore that letter, but... If it was you...<br>
            Here is the code:<br></p>
            {code}<br><br><br></body>
            </html>
            '''
            message.attach(MIMEText(text, 'plain'))
            message.attach(MIMEText(html, 'html'))
            return message.as_string()

        message = get_code_mail(code) if letter_type == "code" else None
        self.__agent.sendmail(from_addr=config.SMTP["login"],
                              to_addrs=to_addrs,
                              msg=message)


if __name__ != '__main__':  # when imported
    print(f"MAIL INIT: {MailAgent.get()}")  # instantly init agent to detect errors as soon as possible
else:
    print("This module can't be used as independent executable.")
