import asyncio

import arrow
import fastapi
import numpy as np
from httpx import AsyncClient

app = fastapi.FastAPI()


async def get_supply(client: AsyncClient):
    res = await client.get('https://etherscan.io/chart/ethersupplygrowth?output=csv')
    return np.array(
        [
            int(float(e.replace('"', '').split(',')[2]))
            for e in res.text.strip().split('\r\n')[-730:]
        ],
        int,
    )


async def get_price(client: AsyncClient):
    res = await client.get('https://etherscan.io/chart/etherprice?output=csv')
    return np.array(
        [
            int(float(e.replace('"', '').split(',')[2]))
            for e in res.text.strip().split('\r\n')[-729:]
        ],
        int,
    )


@app.get('/')
async def root():
    async with AsyncClient(timeout=60) as client:
        supply, price = await asyncio.gather(get_supply(client), get_price(client))
    end = arrow.utcnow().shift(days=-1)
    date = [
        e.format('YY-MM-DD')
        for e in arrow.Arrow.range('day', end.shift(days=-728), end)
    ]
    net_issued = np.diff(supply)
    earnings = -net_issued * price
    ttm = np.convolve(earnings, np.ones(365, int), mode='valid')
    pe = (supply[-365:] * price[-365:] / ttm).astype(int)
    pe[pe < 0] = 0
    return {
        'date': date,
        'net_issued': net_issued.tolist(),
        'earnings': earnings.tolist(),
        'ttm': ttm.tolist(),
        'pe': pe.tolist(),
    }
