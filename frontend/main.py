import requests as r
import streamlit as st

if __name__ == '__main__':
    st.set_page_config('ETH P/E Ratio', layout='wide')
    st.title('ETH P/E Ratio')
    d = r.get('http://127.0.0.1:8000/').json()
    date, net_issued, earnings, ttm, pe = (
        d['date'],
        d['net_issued'],
        d['earnings'],
        d['ttm'],
        d['pe'],
    )
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.metric(
            'Yesterday Net Issued',
            net_issued[-1],
            net_issued[-1] - net_issued[-2],
            'inverse',
        )
    with col_a2:
        st.metric('Yesterday Earnings', earnings[-1], earnings[-1] - earnings[-2])
    with col_a3:
        st.metric('Yesterday TTM Earnings', ttm[-1], ttm[-1] - ttm[-2])
    with col_a4:
        st.metric('Yesterday P/E Ratio', pe[-1], pe[-1] - pe[-2], 'inverse')
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader('Daily Net Issued')
        st.area_chart({'Date': date, 'Net Issued': net_issued}, x='Date')
        st.subheader('Daily Earnings')
        st.area_chart({'Date': date, 'Earnings': earnings}, x='Date')
    with col_b2:
        st.subheader('Daily TTM Earnings')
        st.area_chart({'Date': date[-365:], 'TTM': ttm}, x='Date')
        st.subheader('Daily P/E Ratio')
        st.area_chart({'Date': date[-365:], 'P/E Ratio': pe}, x='Date')
