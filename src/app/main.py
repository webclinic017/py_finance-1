from pkgs.portfolio import PortofolioDescription
from tinydb import TinyDB
from worker import create_task, beta_portfolio, ticker_info_task
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.encoders import jsonable_encoder
import json

db = TinyDB('/data/db.json')
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/beta/")
def betas(description: PortofolioDescription):

    task = beta_portfolio.delay(json.dumps(jsonable_encoder(description)))
    description.task_id = task.id
    db.insert(description.dict())
    return description


@app.post("/portfolio/")
def portfolio(components: PortofolioDescription):

    task = create_task.delay(components.json())
    components.task_id = task.id
    db.insert(components.dict())
    return components

@app.get("/ticker_info")
def ticker_info(q: Optional[List[str]] = Query(None)):
    query_ticker = {'q': q}

    for s in q:
        task = ticker_info_task.delay(s)
    return query_ticker

