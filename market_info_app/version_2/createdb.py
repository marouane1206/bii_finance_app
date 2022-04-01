from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, VARCHAR, create_engine, UniqueConstraint, DateTime
import Config.config as config


class Stock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(sa_column=Column("symbol", VARCHAR, unique=True))
    name: str
    alpaca_id: str
    exchange: str
    easy_to_borrow: bool
    fractionable: bool
    marginable: bool
    shortable: bool
#    heroes: List["Hero"] = Relationship(back_populates="team")


class Stock_Price(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: Optional[int] = Field(default=None, foreign_key="stock.id")
    date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    open: float
    high: float
    low: float
    close: float
    volume: int
#    team: Optional[Team] = Relationship(back_populates="heroes")
    __table_args__ = (UniqueConstraint("stock_id", "date"),)
    
class Strategy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=None,nullable=False)


class Stock_Strategy(SQLModel, table=True):
    stock_id: Optional[int] = Field(default=None, foreign_key="Stock.id")
    strategy_id: Optional[int] = Field(default=None, foreign_key="Strategy.id")

sqlite_file_name = config.DB_FILE
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
