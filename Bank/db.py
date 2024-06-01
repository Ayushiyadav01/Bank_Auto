from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Time, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import config_db

user = config_db['user']
password = config_db['password']
db = config_db['db']
DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@localhost/{db}"
print(DATABASE_URL)

# Create database engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


class Bank(Base):
    __tablename__ = "BANK"
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(255), nullable=False)
    maintenance_start_time = Column(Time)
    maintenance_end_time = Column(Time)


class AccountHolder(Base):
    __tablename__ = "ACCOUNT_HOLDER"
    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey("BANK.id"))
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    account_holder_name = Column(String(255), nullable=False)
    corporate_id = Column(String(255))
    is_corporate_id = Column(Boolean)
    merchant_id = Column(Integer, ForeignKey("MERCHANT.id"))
    pending_chat_id = Column(Integer)
    last_UTR = Column(String(255))
    last_UTR_chat_id = Column(Integer)
    balance_limit = Column(DECIMAL(10, 2))
    gap_range = Column(Integer)
    min_balance = Column(DECIMAL(10, 2))
    is_paused = Column(Boolean)
    bank = relationship("Bank")
    merchant = relationship("Merchant")


class Merchant(Base):
    __tablename__ = "MERCHANT"
    id = Column(Integer, primary_key=True, index=True)
    merchant_name = Column(String(255), nullable=False)
    chat_id = Column(Integer)
    pending_chat_id = Column(Integer)
    client_id = Column(Integer, ForeignKey("CLIENT.id"))


class Client(Base):
    __tablename__ = "CLIENT"
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=False)


# Create all tables
Base.metadata.create_all(bind=engine)
