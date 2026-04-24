from sqlalchemy import Column, Integer, String, Float
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    description = Column(String, nullable=False, default="")
