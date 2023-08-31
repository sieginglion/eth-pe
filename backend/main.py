import asyncio
import os

import arrow
import asyncache
import cachetools
import dotenv
import fastapi
import httpx
import numpy as np

dotenv.load_dotenv()

PROXY = os.getenv('PROXY') or None

PRICE_CSV_URL = 'https://etherscan.io/chart/etherprice?output=csv'
SUPPLY_CSV_URL = 'https://etherscan.io/chart/ethersupplygrowth?output=csv'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

app = fastapi.FastAPI()


@asyncache.cached(cachetools.TTLCache(maxsize=2, ttl=3600))
async def get_csv(url: str):
    async with httpx.AsyncClient(
        headers={'User-Agent': USER_AGENT}, proxies=PROXY, timeout=60
    ) as client:
        return (await client.get(url)).text


def parse_csv(csv: str):
    lines = csv.rstrip().replace('\r', '').split('\n')[1:]
    return np.array([float(l.replace('"', '').split(',')[2]) for l in lines], int)


async def get_supply():
    return parse_csv(await get_csv(SUPPLY_CSV_URL))[-730:]


async def get_price():
    return parse_csv(await get_csv(PRICE_CSV_URL))[-729:]


async def get_end_date():
    csv = await get_csv(SUPPLY_CSV_URL)
    line = csv.rstrip().replace('\r', '').split('\n')[-1]
    return arrow.get(int(line.replace('"', '').split(',')[1]), tzinfo='UTC')


@app.get('/')
async def root():
    supply, price = await asyncio.gather(get_supply(), get_price())
    end_date = await get_end_date()
    date = [
        e.format('YY-MM-DD')
        for e in arrow.Arrow.range('day', end_date.shift(days=-728), end_date)
    ]
    net_issuance = np.diff(supply)
    earnings = -net_issuance * price
    ttm = np.convolve(earnings, np.ones(365, int), 'valid')
    pe = (supply[-365:] * price[-365:] / ttm).astype(int)
    pe[pe < 0] = 0
    return {
        'date': date,
        'net_issuance': net_issuance.tolist(),
        'earnings': earnings.tolist(),
        'ttm': ttm.tolist(),
        'pe': pe.tolist(),
    }
