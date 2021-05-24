# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ba

DATABASE_URL = "postgresql+asyncpg://postgres:12345678kds@localhost:5432/SPARSO"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(engine)


async def connect_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def session(*args, **kwargs):
    async with Session.begin() as session:
        session.add(*args, **kwargs)
