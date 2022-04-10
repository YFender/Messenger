from smtplib import SMTP_SSL

email_server = SMTP_SSL("smtp.mail.ru", 465)
email_server.sendmail()
print(email_server.)
