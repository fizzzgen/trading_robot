import smtplib
import datetime
import time

important_aggregator = []
aggregator = []
latest_important = 0.0
latest = 0.0

mail = 'fizzzgen@yandex.ru'
password = '48674867'

def send_emails(title,msg):
    server = smtplib.SMTP_SSL('smtp.yandex.com:465')
    server.login(mail,password)
    server.auth_plain()
    message = 'Subject: {}\n\n{}'.format(title,msg)
    try:
        server.sendmail(mail ,mail,message)
        server.quit()
        print('E-mails successfully sent!')
    except:
        pass

def online_log(text):
    global latest, aggregator
    aggregator.append(text)
    if latest < time.time() - 5 * 60:
        send_emails('TRADE INFO', '\n'.join(aggregator))
        aggregator = []
        latest = time.time()


def online_log_important(text):
    global latest_important, important_aggregator
    important_aggregator.append(text)
    if latest_important < time.time() - 5 * 60:
        send_emails('TRADE IMPORTANT', '\n'.join(important_aggregator))
        important_aggregator = []
        latest_important = time.time()
