import asyncio
import os
from typing import NamedTuple

import arrow
import dotenv
import httpx
import numpy as np
import streamlit as st

dotenv.load_dotenv()

PROXY = os.getenv('PROXY') or None
COFFEE_URL = os.getenv('COFFEE_URL')
WALLET_URL = os.getenv('WALLET_URL')

PRICE_CSV_URL = 'https://etherscan.io/chart/etherprice?output=csv'
SUPPLY_CSV_URL = 'https://etherscan.io/chart/ethersupplygrowth?output=csv'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'


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


class Data(NamedTuple):
    date: list[str]
    net_issuance: list[int]
    earnings: list[int]
    ttm: list[int]
    pe: list[int]


async def async_get_data():
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
    return Data(
        date,
        net_issuance.tolist(),
        earnings.tolist(),
        ttm.tolist(),
        pe.tolist(),
    )


@st.cache_data(ttl=43200)
def get_data():
    return asyncio.run(async_get_data())


def display_header():
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown('### ETH P/E Ratio')
        st.markdown(
            '##### The P/E ratio concept is applicable to a rental property. Even ETH.'
        )
    with col_2:
        st.markdown('### &nbsp;')
        st.markdown(
            f'<h5 style="text-align: right;">Donate me <a href="{WALLET_URL}">gas fee</a> or <a href="{COFFEE_URL}">coffee</a> 🙏',
            True,
        )


def display_metrics(d: Data):
    col_1, col_2, col_3, col_4 = st.columns(4)
    with col_1:
        st.metric(
            'Yesterday Net Issuance',
            f'{d.net_issuance[-1]:,} ETH',
            f'{d.net_issuance[-1] - d.net_issuance[-2]:,} ETH',
            'inverse',
        )
    with col_2:
        st.metric(
            'Yesterday Earnings',
            f'{d.earnings[-1]:,} USD',
            f'{d.earnings[-1] - d.earnings[-2]:,} USD',
        )
    with col_3:
        st.metric(
            'Yesterday TTM Earnings',
            f'{d.ttm[-1]:,} USD',
            f'{d.ttm[-1] - d.ttm[-2]:,} USD',
        )
    with col_4:
        st.metric(
            'Yesterday P/E Ratio',
            f'{d.pe[-1]:,}',
            f'{d.pe[-1] - d.pe[-2]:,}',
            'inverse',
        )


def display_charts(d: Data):
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown('##### Daily Net Issuance')
        st.area_chart({'Date': d.date, 'ETH': d.net_issuance}, x='Date', y='ETH')
        st.markdown('##### Daily Earnings')
        st.area_chart({'Date': d.date, 'USD': d.earnings}, x='Date', y='USD')
    with col_2:
        st.markdown('##### Daily P/E Ratio')
        st.area_chart({'Date': d.date[-365:], 'P/E': d.pe}, x='Date', y='P/E')
        st.markdown('##### Daily TTM Earnings')
        st.area_chart({'Date': d.date[-365:], 'USD': d.ttm}, x='Date', y='USD')


def main():
    st.set_page_config('ETH P/E Ratio', layout='wide')
    data = get_data()
    display_header()
    st.divider()
    display_metrics(data)
    st.divider()
    display_charts(data)


if __name__ == '__main__':
    main()
