import os
from dataclasses import dataclass

import requests as r
import streamlit as st

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8080')


@dataclass
class Data:
    date: list[str]
    net_issuance: list[int]
    earnings: list[int]
    ttm: list[int]
    pe: list[int]


@st.cache_data(ttl=3600)
def get_data():
    return Data(**r.get(BASE_URL + '/').json())


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
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader('Daily Net Issuance')
        st.area_chart({'Date': d.date, 'ETH': d.net_issuance}, x='Date', y='ETH')
        st.subheader('Daily Earnings')
        st.area_chart({'Date': d.date, 'USD': d.earnings}, x='Date', y='USD')
    with col_b2:
        st.subheader('Daily P/E Ratio')
        st.area_chart({'Date': d.date[-365:], 'P/E': d.pe}, x='Date', y='P/E')
        st.subheader('Daily TTM Earnings')
        st.area_chart({'Date': d.date[-365:], 'USD': d.ttm}, x='Date', y='USD')


if __name__ == '__main__':
    st.set_page_config('ETH P/E Ratio', layout='wide')
    st.title('ETH P/E Ratio')
    data = get_data()
    display_metrics(data)
    display_charts(data)
