from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./blockchain.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BlockModel(Base):
    __tablename__ = "blocks"

    id = Column(String, primary_key=True, index=True)
    index = Column(Integer)
    timestamp = Column(Float)
    proof = Column(Integer)
    previous_hash = Column(String)
    # Guardamos o dicionário 'dados'  texto JSON
    dados_json = Column(Text)

# Cria a tabela se não existir
Base.metadata.create_all(bind=engine)