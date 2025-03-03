import requests, os
from .kivDataclass import ChargePayment


def create_charge(charge_payment: ChargePayment):
    url = f"{os.environ['BASE_URL']}/card/v2/charge"
    headers = {
        "content-type": "application/json",
        "x-api-key": os.environ["KBANK_SECRET_KEY"],
    }
    body = charge_payment.to_dict()
    print("body ", body)
    r = requests.post(url, json=body, headers=headers)
    return r.json()
