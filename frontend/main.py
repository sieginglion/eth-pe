import os
from dataclasses import dataclass

import requests as r
import streamlit as st
from streamlit.components.v1 import html as display_html

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


def display_header():
    MD = '''
    ### ETH P/E Ratio
    ##### The P/E ratio concept is applicable to a rental property. Even ETH.
    '''
    HTML = '<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="sieginglion" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>'
    CSS = '''
    <style>
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section > div.block-container.css-z5fcl4.ea3mdgi4 > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div {
            display: flex;
            justify-content: end;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section > div.block-container.css-z5fcl4.ea3mdgi4 > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div {
            gap: 0;
        }
    </style>
    '''
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown(MD)
    with col_2:
        display_html(HTML, 225, 75)
        st.markdown(CSS, True)


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
