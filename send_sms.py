import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
receiver = os.getenv("TWILIO_RECEIVER")
sender = os.getenv("TWILIO_SENDER")

client = Client(account_sid, auth_token)


def price_alerts(message):
    """Sends SMS using Twilio.

    Args:
        message (str): Token pairs e.g. "(3S-BTC/USD: 3.33) (1S-ETH/USD: 2.06) (3S-ETH/USD: 2.99)"
    """
    client.api.account.messages.create(to=receiver, from_=sender, body=message)
