from typing import NamedTuple

import requests as r
import streamlit as st
import os
import dotenv

dotenv.load_dotenv()

WALLET_URL = os.getenv('WALLET_URL')
COFFEE_URL = os.getenv('COFFEE_URL')


class Data(NamedTuple):
    date: list[str]
    net_issuance: list[int]
    earnings: list[int]
    ttm: list[int]
    pe: list[int]


@st.cache_data(ttl=3600)
def get_data():
    return Data(**r.get('http://127.0.0.1:8080/').json())


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
