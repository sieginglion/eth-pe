import asyncio

import aiofiles
import arrow
import fastapi
import numpy as np

app = fastapi.FastAPI()


async def get_end_date():
    async with aiofiles.open('supply.csv') as f:
        csv = await f.read()
    return arrow.get(
        int(csv.rstrip().split('\n')[-1].replace('"', '').split(',')[1]), tzinfo='UTC'
    )


async def get_supply():
    async with aiofiles.open('supply.csv') as f:
        csv = await f.read()
    return np.array(
        [
            float(e.replace('"', '').split(',')[2])
            for e in csv.rstrip().split('\n')[-730:]
        ],
        int,
    )


async def get_price():
    async with aiofiles.open('price.csv') as f:
        csv = await f.read()
    return np.array(
        [
            float(e.replace('"', '').split(',')[2])
            for e in csv.rstrip().split('\n')[-729:]
        ],
        int,
    )


@app.get('/')
async def root():
    end_date, supply, price = await asyncio.gather(
        get_end_date(), get_supply(), get_price()
    )
    date = [
        e.format('YY-MM-DD')
        for e in arrow.Arrow.range('day', end_date.shift(days=-728), end_date)
    ]
    net_issuance = np.diff(supply)
    earnings = -net_issuance * price
    ttm = np.convolve(earnings, np.ones(365, int), mode='valid')
    pe = (supply[-365:] * price[-365:] / ttm).astype(int)
    pe[pe < 0] = 0
    return {
        'date': date,
        'net_issuance': net_issuance.tolist(),
        'earnings': earnings.tolist(),
        'ttm': ttm.tolist(),
        'pe': pe.tolist(),
    }
