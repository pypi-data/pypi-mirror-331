from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Optional
import requests


class SourceType(str, Enum):
    CARD = "card"
    ALIPAY = "alipay"


class Mode(str, Enum):
    FULLPAN = "fullpan"
    TOKEN = "token"
    CUSTOMER = "customer"
    REGISTER3D = "register3D"


@dataclass
class Card:
    name: str
    number: str
    expmonth: str
    expyear: str
    cvv: str

    def to_dict(self):
        return {
            "name": self.name,
            "number": self.number,
            "expmonth": self.expmonth,
            "expyear": self.expyear,
            "cvv": self.cvv,
        }


@dataclass
class Customer:
    customer_id: str

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
        }


@dataclass
class ChargePayment:
    amount: float
    description: str
    source_type: SourceType
    mode: Mode
    token: str
    save_card: str
    reference_order: str
    ref_1: str  # order id
    ref_2: str  # customer id
    customer: Customer
    card: Optional[Card] = None
    currency: str = "THB"

    def to_dict(self):
        return {
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "source_type": self.source_type.value,
            "mode": self.mode.value,
            "token": self.token,
            "save_card": self.save_card,
            "reference_order": self.reference_order,
            "ref_1": self.ref_1,
            "ref_2": self.ref_2,
            "card": self.card.to_dict() if self.card else None,
            "customer": self.customer.to_dict(),
        }
