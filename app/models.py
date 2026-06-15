from sqlalchemy import Column, Integer, String
from app.database import Base

class PokemonModel(Base):
    __tablename__ = "pokemons"

    # ID oficial que vem direto da PokéAPI (será nossa chave primária)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    height = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    
    # Armazenaremos os tipos como texto separado por vírgula (Ex: "electric,steel")
    types = Column(String, nullable=False)
    
    # Armazenaremos os links das imagens direto nas colunas
    front_default = Column(String, nullable=True)
    back_default = Column(String, nullable=True)