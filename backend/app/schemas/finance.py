from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.pydantic_types import GDate

class AccountBase(BaseModel):
    name: str
    bank_name: Optional[str] = None
    sheba_number: Optional[str] = None
    current_balance: float = 0
    register_date: Optional[GDate] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    bank_name: Optional[str] = None
    sheba_number: Optional[str] = None
    current_balance: Optional[float] = None
    register_date: Optional[GDate] = None

class AccountRead(AccountBase):
    id: int
    owner_id: int
    created_at: datetime
    transaction_count: int = 0
    total_deposits: float = 0
    total_withdrawals: float = 0

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    transaction_date: Optional[GDate] = None
    transaction_type: str
    amount: float = 0
    description: Optional[str] = None
    balance_after: Optional[float] = 0

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    account_id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True