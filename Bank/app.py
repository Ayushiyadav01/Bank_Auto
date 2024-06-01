from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import List
import threading
import time
from db import SessionLocal, Bank, AccountHolder, Merchant, Client

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BankCreate(BaseModel):
    bank_name: str
    maintenance_start_time: str
    maintenance_end_time: str


class AccountHolderCreate(BaseModel):
    bank_id: int
    username: str
    password: str
    account_holder_name: str
    corporate_id: str = None
    is_corporate_id: bool = False
    merchant_id: int
    pending_chat_id: int = None
    last_UTR: str = None
    last_UTR_chat_id: int = None
    balance_limit: float
    gap_range: int
    min_balance: float
    is_paused: bool = False


class AccountHolderUpdate(BaseModel):
    value: str


class MerchantCreate(BaseModel):
    merchant_name: str
    chat_id: int
    pending_chat_id: int
    client_id: int


class ClientCreate(BaseModel):
    client_name: str


@app.get("/banks/", response_model=List[str])
def read_banks(db: Session = Depends(get_db)):
    """
    To get the bank details
    :param db:
    :return:
    """
    try:
        banks = db.query(Bank).all()
        return [bank.bank_name for bank in banks]
    except Exception as e:
        print(e)


@app.post("/add_bank", response_model=BankCreate)
def add_bank(bank: BankCreate, db: Session = Depends(get_db)):
    try:
        db_bank = Bank(
            bank_name=bank.bank_name,
            maintenance_start_time=bank.maintenance_start_time,
            maintenance_end_time=bank.maintenance_end_time
        )
        db.add(db_bank)
        db.commit()
        db.refresh(db_bank)
        return db_bank
    except Exception as e:
        print(e)


@app.delete("/remove_bank/{bank_id}", response_model=dict)
def remove_bank(bank_id: int, db: Session = Depends(get_db)):
    try:
        db_bank = db.query(Bank).filter(Bank.id == bank_id).first()
        if db_bank is None:
            raise HTTPException(status_code=404, detail="Bank not found")
        db.delete(db_bank)
        db.commit()
        return {"detail": "Bank deleted"}
    except Exception as e:
        print(e)


@app.get("/account_holders/", response_model=List[str])
def read_account_holders(db: Session = Depends(get_db)):
    try:
        account_holders = db.query(AccountHolder).all()
        return [holder.username for holder in account_holders]
    except Exception as e:
        print(e)


@app.post("/add_account_holder", response_model=AccountHolderCreate)
def add_account_holder(account_holder: AccountHolderCreate, db: Session = Depends(get_db)):
    try:
        db_account_holder = AccountHolder(
            bank_id=account_holder.bank_id,
            username=account_holder.username,
            password=account_holder.password,
            account_holder_name=account_holder.account_holder_name,
            corporate_id=account_holder.corporate_id,
            is_corporate_id=account_holder.is_corporate_id,
            merchant_id=account_holder.merchant_id,
            pending_chat_id=account_holder.pending_chat_id,
            last_UTR=account_holder.last_UTR,
            last_UTR_chat_id=account_holder.last_UTR_chat_id,
            balance_limit=account_holder.balance_limit,
            gap_range=account_holder.gap_range,
            min_balance=account_holder.min_balance,
            is_paused=account_holder.is_paused
        )
        db.add(db_account_holder)
        db.commit()
        db.refresh(db_account_holder)
        return db_account_holder
    except Exception as e:
        print(e)


@app.delete("/remove_account_holder/{account_holder_id}", response_model=dict)
def remove_account_holder(account_holder_id: int, db: Session = Depends(get_db)):
    try:
        db_account_holder = db.query(AccountHolder).filter(AccountHolder.id == account_holder_id).first()
        if db_account_holder is None:
            raise HTTPException(status_code=404, detail="Account holder not found")
        db.delete(db_account_holder)
        db.commit()
        return {"detail": "Account holder deleted"}
    except Exception as e:
        print(e)


@app.get("/merchants/", response_model=List[str])
def read_merchants(db: Session = Depends(get_db)):
    try:
        merchants = db.query(Merchant).all()
        return [merchant.merchant_name for merchant in merchants]
    except Exception as e:
        print(e)


@app.delete("/remove_merchant/{merchant_id}", response_model=dict)
def remove_merchant(merchant_id: int, db: Session = Depends(get_db)):
    try:
        db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if db_merchant is None:
            raise HTTPException(status_code=404, detail="Merchant not found")
        db.delete(db_merchant)
        db.commit()
        return {"detail": "Merchant deleted"}
    except Exception as e:
        print(e)


@app.post("/add_merchant", response_model=MerchantCreate)
def add_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    try:
        db_merchant = Merchant(
            merchant_name=merchant.merchant_name,
            chat_id=merchant.chat_id,
            pending_chat_id=merchant.pending_chat_id,
            client_id=merchant.client_id
        )
        db.add(db_merchant)
        db.commit()
        db.refresh(db_merchant)
        return db_merchant
    except Exception as e:
        print(e)


@app.post("/add_client", response_model=ClientCreate)
def add_client(client: ClientCreate, db: Session = Depends(get_db)):
    try:
        db_client = Client(client_name=client.client_name)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except Exception as e:
        print(e)


@app.delete("/remove_client/{client_id}", response_model=dict)
def remove_client(client_id: int, db: Session = Depends(get_db)):
    try:
        db_client = db.query(Client).filter(Client.id == client_id).first()
        if db_client is None:
            raise HTTPException(status_code=404, detail="Client not found")
        db.delete(db_client)
        db.commit()
        return {"detail": "Client deleted"}
    except Exception as e:
        print(e)


@app.put("/update_account_holder/{account_holder_id}")
def update_account_holder(account_holder_id: int, column: str, updates: AccountHolderUpdate,
                          db: Session = Depends(get_db)):
    try:
        if column not in AccountHolder.__table__.columns:
            raise HTTPException(status_code=400, detail="Invalid column name")

        db.execute(update(AccountHolder).where(AccountHolder.id == account_holder_id).values({column: updates.value}))
        db.commit()

        return {"message": f"{column} updated successfully"}
    except Exception as e:
        print(e)


def print_account_holder_details(username: str, password: str, stop_event):
    try:
        while not stop_event.is_set():
            print(f"Username: {username}, Password: {password}")
            time.sleep(5)
    except Exception as e:
        print(e)


threads = {}
threads_lock = threading.Lock()


def check_account_holders():
    while True:
        db = SessionLocal()
        try:
            account_holders = db.query(AccountHolder).all()
            with threads_lock:
                for account_holder in account_holders:
                    if not account_holder.is_paused and account_holder.username not in threads:
                        stop_event = threading.Event()
                        thread = threading.Thread(target=print_account_holder_details,
                                                  args=(account_holder.username, account_holder.password, stop_event))
                        threads[account_holder.username] = (thread, stop_event)
                        thread.start()

                    if account_holder.is_paused and account_holder.username in threads:
                        _, stop_event = threads.pop(account_holder.username)
                        stop_event.set()
        finally:
            db.close()
        time.sleep(5)


@app.on_event("startup")
def startup_event():
    background_thread = threading.Thread(target=check_account_holders)
    background_thread.start()
