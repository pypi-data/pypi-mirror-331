from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from telethon.tl.types import User
# import pg8000
import sys






# SYSTEM AUTH
sqlURi = "postgresql+pg8000://neondb_owner:npg_rQ4R5uLwPoNg@ep-dawn-paper-a1i8uyqu-pooler.ap-southeast-1.aws.neon.tech/neondb"
engine = create_engine(sqlURi, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
class Authorization(Base):
    __tablename__ = "bot_authorization"

    id = Column(Integer, primary_key=True, index=True)
    is_authorized = Column(Boolean, default=False, nullable=False)
Base.metadata.create_all(bind=engine)
def bachahaiYaNahi():
    session = SessionLocal()
    auth = session.query(Authorization).first()
    if auth and auth.is_authorized:
        print("✅ Authorization granted. Running bot...")
    else:
        print("⛔ Authorization denied. Exiting script.")
        sys.exit() 
    session.close()
# bachahaiYaNahi()







class RequiredChannels(Base):
    __tablename__ = "required_channels"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    invite_links = Column(JSON, nullable=False)
Base.metadata.create_all(bind=engine)
DEFAULT_CHANNELS = [
    "https://t.me/+KSlqCYSiHqdkMGU9",
    "https://t.me/+Q1bW081uXApmYmI1",
    "https://t.me/+EeevHhSv9ExlOTI1"
]
def storindegf():
    session = SessionLocal()
    existing = session.query(RequiredChannels).filter_by(name="required_channels").first()
    
    if not existing:
        new_entry = RequiredChannels(name="required_channels", invite_links=DEFAULT_CHANNELS)
        session.add(new_entry)
        session.commit()
        print("✅ Default required channels stored.")
    
    session.close()
storindegf()
def JARURATNIKALDO():
    session = SessionLocal()
    
    document = session.query(RequiredChannels).filter_by(name="required_channels").first()
    
    session.close()
    
    return document.invite_links if document else []









class ScamChannels(Base):
    __tablename__ = "scam_channels"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    invite_links = Column(JSON, nullable=False) 
Base.metadata.create_all(bind=engine)

DEFAULT_SCAM_CHANNELS = [
    "https://t.me/avoid",
    "https://t.me/trustedscams",
    "https://t.me/ScamDatabaseLogs"
]
def storinscamde():
    session = SessionLocal()
    existing = session.query(ScamChannels).filter_by(name="scam_channels").first()
    if not existing:
        new_entry = ScamChannels(name="scam_channels", invite_links=DEFAULT_SCAM_CHANNELS)
        session.add(new_entry)
        session.commit()
        print("✅ Scam-reporting channels stored in PostgreSQL.")
    session.close()
storinscamde()
def JHANTUNIKALOREEE():
    """Fetch scam-reporting channels from PostgreSQL."""
    session = SessionLocal()
    document = session.query(ScamChannels).filter_by(name="scam_channels").first()
    session.close()
    return document.invite_links if document else []










class UserActivity(Base):
    __tablename__ = "user_activity"

    user_id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
Base.metadata.create_all(bind=engine)
async def YOUAREREGISTERED(event):
    """Records the self-bot user's ID, name, and username in PostgreSQL, avoiding duplicates."""
    session = SessionLocal()
    me = await event.client.get_me() 
    existing_user = session.query(UserActivity).filter_by(user_id=me.id).first()
    if not existing_user:
        new_user = UserActivity(
            user_id=me.id,
            first_name=me.first_name,
            username=me.username if me.username else "No Username",
            is_premium=me.premium if isinstance(me, User) and hasattr(me, "premium") else False
        )
        session.add(new_user)
        session.commit()
        print(f"✅ Registered Self-Bot User: {me.id} - {me.first_name} (@{me.username})")
    session.close()
