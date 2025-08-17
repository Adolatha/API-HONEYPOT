from fastapi import APIRouter, Request, HTTPException, Query, Body, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging
import re
import asyncio
import random

from app.db_decoy import AsyncDecoySession
from app.decoy_models import (
    DecoyUser, DecoyCreditCard, DecoyBankAccount,
    DecoyPayroll, DecoyAPIKey, DecoySecret, DecoyContract, DbChangeLog
)
from app.decoy_schemas import (
    UserOut, CreditCardOut, BankAccountOut,
    PayrollOut, APIKeyOut, SecretOut, ContractOut
)

SQLI_SIGNS = re.compile(r"('|\")|(\bOR\b|\bAND\b)|(--|#|/\*)|(\bUNION\b)|(\bSELECT\b)|(\bUPDATE\b)|(\bINSERT\b)|(\bDELETE\b)|(\bDROP\b)|(;)", re.IGNORECASE)

def looks_like_sqli(val: str) -> bool:
    if not val:
        return False
    return bool(SQLI_SIGNS.search(val))

router = APIRouter(prefix="/webhoneypot", tags=["webhoneypot"])
logger = logging.getLogger("honeypot_db")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/decoy_db.log")
logger.addHandler(handler)

async def log_and_run(sql: str, src_ip: str):
    async with AsyncDecoySession() as s:
        await s.execute(
            text("INSERT INTO db_changelog (table_name, query, timestamp, src_ip) VALUES (:t, :q, :ts, :ip)"),
            {"t": "RAW", "q": sql[:1000], "ts": datetime.utcnow(), "ip": src_ip}
        )
        await s.commit()
    logger.info(f"{src_ip} {sql}")
    async with AsyncDecoySession() as s:
        try:
            res = await s.execute(text(sql))
            return [dict(r) for r in res.mappings().all()]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.__context__ or e))

async def log_only(sql: str, src_ip: str):
    async with AsyncDecoySession() as s:
        await s.execute(
            text("INSERT INTO db_changelog (table_name, query, timestamp, src_ip) VALUES (:t, :q, :ts, :ip)"),
            {"t": "RAW", "q": sql[:1000], "ts": datetime.utcnow(), "ip": src_ip}
        )
        await s.commit()
    logger.info(f"{src_ip} {sql}")


@router.get("/users", response_model=list[UserOut])
async def get_users(name: str = Query("", description="SQLi trap")):
    sql = f"SELECT * FROM users WHERE full_name LIKE '%{name}%'"
    return await log_and_run(sql, src_ip="unknown")

@router.get("/credit-cards", response_model=list[CreditCardOut])
async def get_cards(request: Request, email: str = Query("", description="SQLi trap")):
    src_ip = request.client.host if request.client else "unknown"
    probe_sql = "SELECT c.* FROM credit_cards c JOIN users u ON u.id=c.user_id WHERE u.email='" + email + "'"
    if not looks_like_sqli(email):
        await asyncio.sleep(random.uniform(0.8, 2.0))
        await log_and_run(probe_sql, src_ip=src_ip)
        return []
    rows = await log_and_run(probe_sql, src_ip=src_ip)
    redacted = []
    for r in rows:
        d = dict(r)
        d["card_number"] = ""
        redacted.append(d)
    return redacted

ERROR_MESSAGES = [
    "sqlite3.OperationalError: near \"'\": syntax error",
    "sqlite3.OperationalError: unrecognized token",
    "sqlalchemy.exc.ProgrammingError: You can only execute one statement at a time.",
    "sqlalchemy.exc.DatabaseError: file is encrypted or is not a database",
    "psycopg2.errors.SyntaxError: syntax error at or near \"UNION\"",
    "mysql.connector.errors.ProgrammingError: 1064 (42000): You have an error in your SQL syntax",
]

@router.post("/raw-query")
async def raw_query(request: Request, body: dict = Body(...)):
    sql = body.get("sql", "")
    if not isinstance(sql, str) or not sql.strip():
        raise HTTPException(status_code=400, detail="Provide JSON with a non-empty 'sql'.")
    src_ip = request.client.host if request.client else "unknown"
    await log_only(sql, src_ip)
    await asyncio.sleep(random.uniform(0.5, 2.0))
    raise HTTPException(status_code=500, detail=random.choice(ERROR_MESSAGES))
