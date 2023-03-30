import pandas as pd
import plotly.express as px
import streamlit as st
import simplejson as json
import requests
import streamlit_lottie
from streamlit_lottie import st_lottie
import toml


#https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Sales Dashboard',
                   page_icon=":bar_chart:",
                   layout='wide',
)

config = toml.load("config.toml")
st.write(config)



@st.cache_data
def get_data_from_excel():
  
    url = 'https://raw.githubusercontent.com/LuannSantoss/Sales-Dashboard/main/supermarkt_sales.xlsx'
    df = pd.read_excel(url, sheet_name='Sales')


    df = df.drop(df.index[:2])
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    df = df.reset_index(drop=True)
    df = df.dropna(axis=1, how='all')

    #Adding 'hour' column to dataframe
    df['hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    return df

df = get_data_from_excel()


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_hello = load_lottieurl('https://assets9.lottiefiles.com/packages/lf20_3vbOcw.json')

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique(),
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

df_selection = df.query(
    "City == @city & Customer_type ==@customer_type & Gender == @gender"
)

# ---- MAINPAGE ----
st.title(":bar_chart: Sales Dashboard")

st_lottie(lottie_hello, key='hello!', width=250, height=250)

st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("""---""")

st.dataframe(df_selection)

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby("Product line")["Total"].sum().sort_values()

fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#3C2F2F"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)




# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby("hour")["Total"].sum().sort_values()

fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#3C2F2F"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

#--- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;} 
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)


