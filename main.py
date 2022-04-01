from enum import Enum
from fastapi import FastAPI

class InvestmentType(str, Enum):
    Intraday_Day_Trading = "Intraday_Day_Trading"
    Intraday_Scalping = "Intraday_Scalping"
    Short_Term_EOD_Trading = "Short_Term_EOD_Trading"    
    Short_Term_Swing_Trading = "Short_Term_Swing_Trading"
    Short_Term_Position_Trading = "Short_Term_Position_Trading"
    Mid_Term_EOW_Trading = "Mid_Term_EOW_Trading"
    Mid_Term_Breakout_Trading = "Mid_Term_Breakout_Trading"
    Mid_Term_Trading_Reversal = "Mid_Term_Trading_Reversal"
    Mid_Term_Momentum_Trading = "Mid_Term_Momentum_Trading"
    Mid_Term_Trend_Following = "Mid_Term_Trend_Following"
    Long_Term_EOM_Trading = "Long_Term_EOM_Trading" 
    Long_Term_Trend_Trading = "Long_Term_Trend_Trading"

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def root():
    return {"bii_finance_API": "Welcome to the High Tech bii_finance_api"}


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/models/{InvestmentType}")
async def get_invest_type(invest_type: InvestmentType):
    if invest_type == InvestmentType.Intraday_Day_Trading:
        return {"invest_type": invest_type, "message": "Intraday Day Trading"}

    if invest_type == InvestmentType.Intraday_Scalping:
        return {"invest_type": invest_type, "message": "Intraday Scalping"}

    return {"invest_type": invest_type, "message": "Have some residuals"}

@app.get("/models/{invest_type}/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
