import os, requests

# Reading environment variables and generating a Telegram Bot API URL
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_USER_ID = os.environ['TELEGRAM_USER_ID']
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_TOKEN)

def notify_telegram(message: str):
    # Payload to be set via POST method to Telegram Bot API
    payload = {
        "text": message.encode("utf8"),
        "chat_id": TELEGRAM_USER_ID,
        "parse_mode": "html"
    }

    # Posting the payload to Telegram Bot API
    requests.post(TELEGRAM_URL, payload)

def alarm_ec2(started: list, stopped: list):
    if len(started) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('EC2 Schedule')
        message_alarm += "\n🚀 Started Instances\n\n"
        for i in started:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)
    
    if len(stopped) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('EC2 Schedule')
        message_alarm += "\n⛔ Stopped Instances\n\n"
        for i in stopped:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)

def alarm_rds(started: list, stopped: list):
    if len(started) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('RDS Schedule')
        message_alarm += "\n🚀 Started Instances\n\n"
        for i in started:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)
    
    if len(stopped) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('RDS Schedule')
        message_alarm += "\n⛔ Stopped Instances\n\n"
        for i in stopped:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)


def alarm_ecs(started: list, stopped: list):
    if len(started) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('ECS Schedule')
        message_alarm += "\n🚀 Started Services\n\n"
        for i in started:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)
    
    if len(stopped) > 0:
        message_alarm = "🔔 <strong>{}</strong> 🔔\n".format('ECS Schedule')
        message_alarm += "\n⛔ Stopped Services\n\n"
        for i in stopped:
            message_alarm += "- {}\n".format(i)
        
        notify_telegram(message=message_alarm)