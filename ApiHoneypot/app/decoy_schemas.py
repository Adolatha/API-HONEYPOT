from pydantic import BaseModel
from datetime import datetime

def orm_cfg():
    return {"from_attributes": True}

class UserOut(BaseModel):
    id: int 
    full_name: str
    email: str
    ssn: str
    last_login: datetime
    two_fa_secret: str
    class Config:
        from_attributes = True

class CreditCardOut(BaseModel):
    id: int
    user_id: int
    card_number: str
    expiry: str
    cvv: str
    billing_address: str
    class Config:
        from_attributes = True
        
class BankAccountOut(BaseModel):
    id: int; user_id: int; account_number: str
    routing_number: str; balance: float; account_type: str
    model_config = orm_cfg()

class PayrollOut(BaseModel):
    id: int; user_id: int; salary: int
    bonus: int; tax_withheld: int; pay_date: datetime
    model_config = orm_cfg()

class APIKeyOut(BaseModel):
    id: int; service: str; key_plaintext: str
    created_at: datetime; expires_at: datetime
    model_config = orm_cfg()

class SecretOut(BaseModel):
    id: int; name: str; value: str
    classification: str; last_modified: datetime
    model_config = orm_cfg()

class ContractOut(BaseModel):
    id: int; title: str; party_a: str; party_b: str
    content_snippet: str; signed_on: datetime
    model_config = orm_cfg()
