import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
receiver = os.getenv('TWILIO_RECEIVER')
sender = os.getenv('TWILIO_SENDER')

client = Client(account_sid, auth_token)

def price_alerts(message):
    client.api.account.messages.create(
    to=receiver,
    from_=sender,
    body=message)
    


