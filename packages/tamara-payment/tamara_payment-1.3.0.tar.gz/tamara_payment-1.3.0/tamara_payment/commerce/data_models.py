from dataclasses import dataclass


@dataclass
class RequestBody():
    shipping_amount: str
    total_tax_amount: str
    basket_items: list
    shipping_address: dict
    billing_address: dict
