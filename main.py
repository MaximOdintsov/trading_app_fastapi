from datetime import datetime
from enum import Enum

import fastapi
import pydantic
from typing import List, Optional

from fastapi import FastAPI
from fastapi import exceptions
from fastapi import responses
from fastapi import encoders

app = FastAPI(
    title='Trading App'
)


@app.exception_handler(exceptions.ValidationError)
def validation_error_response(request: fastapi.Request, exc: exceptions.ValidationError):
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=encoders.jsonable_encoder({'detail': exc.errors()})
    )


fake_users = [
    {'id': 1, 'role': 'admin', 'name': ['John']},
    {'id': 2, 'role': 'investor', 'name': 'Andrey'},
    {'id': 3, 'role': 'trader', 'name': 'Alex'},
    {'id': 4, 'role': 'trader', 'name': 'Justin', 'degree': [
        {'id': 1, 'created_at': datetime.now(), 'type_degree': 'expert'}
    ]},
]


class DegreeType(Enum):
    newbie = 'newbie'
    expert = 'expert'


class Degree(pydantic.BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType


class User(pydantic.BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []


@app.get('/users/{user_id}', response_model=List[User])
def get_user(user_id: int):
    return [user for user in fake_users if user.get('id') == user_id]


fake_trades = [
    {'id': 1, 'user_id': 1, 'currency': 'BTC', 'side': 'buy', 'amount': 2.5},
    {'id': 2, 'user_id': 2, 'currency': 'BTC', 'side': 'buy', 'amount': 2.3},
    {'id': 3, 'user_id': 2, 'currency': 'BTC', 'side': 'buy', 'amount': 4},
    {'id': 4, 'user_id': 2, 'currency': 'ETH', 'side': 'sell', 'amount': 5.5},
    {'id': 5, 'user_id': 1, 'currency': 'BTC', 'side': 'buy', 'amount': 1.9},
    {'id': 6, 'user_id': 1, 'currency': 'ETH', 'side': 'sell', 'amount': 2.1},
    {'id': 7, 'user_id': 2, 'currency': 'BTC', 'side': 'buy', 'amount': 7},
    {'id': 8, 'user_id': 2, 'currency': 'ETH', 'side': 'sell', 'amount': 5.211},
    {'id': 9, 'user_id': 1, 'currency': 'BTC', 'side': 'sell', 'amount': 1.33},
    {'id': 10, 'user_id': 1, 'currency': 'ETH', 'side': 'sell', 'amount': 6},
]


@app.get('/trades/')
def get_trades(limit: int = 5, offset: int = 0):
    return fake_trades[offset:][:limit]


@app.post('/users/{user_id}')
def change_user_name(user_id: int, new_name: str):
    current_user = list(filter(lambda user: user.get('id') == user_id, fake_users))[0]
    current_user['name'] = new_name
    return {'status': 200, 'user': current_user}


class Trade(pydantic.BaseModel):
    id: int
    user_id: int
    currency: str = pydantic.Field(max_length=5)
    side: str
    amount: float = pydantic.Field(ge=0)


@app.post('/trades/')
def add_trades(trades: List[Trade]):
    fake_trades.extend(trades)
    return {'status': 200, 'data': fake_trades}