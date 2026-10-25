"""Best effort failure notification; GitHub Actions failure notifications are the fallback."""
import email.message
import os
import smtplib
import ssl

required = ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD','MAIL_FROM','MAIL_TO']
if not all(os.environ.get(k) for k in required):
    raise SystemExit('SMTP configuration incomplete; check GitHub Actions failure notifications')
msg = email.message.EmailMessage()
msg['Subject'] = 'GitHub AI 报告任务失败，请检查'
msg['From'] = os.environ['MAIL_FROM']
msg['To'] = os.environ['MAIL_TO']
msg.set_content('报告采集、生成、部署或邮件步骤未完成。\n运行记录：' + os.environ.get('RUN_URL',''))
port = int(os.environ.get('SMTP_PORT') or '465')
if port == 465:
    client = smtplib.SMTP_SSL(os.environ['SMTP_HOST'], port, context=ssl.create_default_context(), timeout=60)
else:
    client = smtplib.SMTP(os.environ['SMTP_HOST'], port, timeout=60)
    client.ehlo(); client.starttls(context=ssl.create_default_context()); client.ehlo()
with client:
    client.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
    client.send_message(msg)
