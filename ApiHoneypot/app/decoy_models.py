from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from .db_decoy import DecoyBase

class DecoyUser(DecoyBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    ssn = Column(String(11))
    hashed_password = Column(String(128))
    last_login = Column(DateTime)
    two_fa_secret = Column(String(64))

class DecoyCreditCard(DecoyBase):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_number = Column(String(20))
    expiry = Column(String(7))
    cvv = Column(String(4))
    billing_address = Column(String(200))

class DecoyBankAccount(DecoyBase):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_number = Column(String(34))
    routing_number = Column(String(9))
    balance = Column(Float)
    account_type = Column(String(20))

class DecoyPayroll(DecoyBase):
    __tablename__ = "payroll"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    salary = Column(Integer)
    bonus = Column(Integer)
    tax_withheld = Column(Integer)
    pay_date = Column(DateTime)

class DecoyAPIKey(DecoyBase):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50))
    key_plaintext = Column(String(64))
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

class DecoySecret(DecoyBase):
    __tablename__ = "secrets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    value = Column(String(256))
    classification = Column(String(20))
    last_modified = Column(DateTime)

class DecoyContract(DecoyBase):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150))
    party_a = Column(String(100))
    party_b = Column(String(100))
    content_snippet = Column(String(200))
    signed_on = Column(DateTime)

class DbChangeLog(DecoyBase):
    __tablename__ = "db_changelog"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50))
    query = Column(String(1000))
    timestamp = Column(DateTime)
    src_ip = Column(String(45))
