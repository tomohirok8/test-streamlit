import pandas as pd
import datetime as dt
import pandas_datareader.data as web
import altair as alt
import streamlit as st

apikey = 'C6T7IWRUOLS8TM5O'

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# 株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 100, 30)

st.write(f"""
### 過去 **{days}日間** の株価
""")

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        hist = web.DataReader(tickers[company], 'av-daily', start, end, api_key=apikey)
        hist = hist[['close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 5000.0, (0.0, 5000.0)
    )

    tickers = {
        'apple': 'AAPL',
        'facebook': 'FB',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    companies = st.multiselect(
        '会社名を選択してください。',
        list(tickers.keys()),
        ['google', 'amazon', 'facebook', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        select_list = []
        for company in companies:
            select_list.append([company,tickers[company]])
        select_tickers = dict(select_list)

        st.write(select_tickers)

        df = get_data(days, select_tickers)

        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['index']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="index:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )

