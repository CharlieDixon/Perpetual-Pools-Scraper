import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

def price_alerts(message):
    client.api.account.messages.create(
    to="+447875093492",
    from_="+447897033129",
    body=message)
# twilio phone-numbers:buy:mobile --country-code GB --sms-enabled
# SID                                 Phone Number   Friendly Name
# PNf7963ed19d26b6e07c8f429f734c723c  +447897033129  447897033129