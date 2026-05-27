import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO



####################################
# Page configuration first
####################################

st.set_page_config(
    page_title="Kitchen Level PNL Dashboard",
    layout="wide"
)

st.title("Kitchen Level PNL Dashboard")


####################################
# Load data from given excel file
####################################

@st.cache_data
def load_data():
    df = pd.read_excel(
        "Kitchen Profit & Loss Data.xlsx",
        header=1
    )
    # Derived metrics
    df["GM_PERCENT"] = (
        df["GROSS MARGIN"] / df["NET REVENUE"]
    ) * 100

    df["EBITDA_PERCENT"] = (
        df["KITCHEN EBITDA"] / df["NET REVENUE"]
    ) * 100

    return df

## after adding columns , load data into dataframe
df = load_data()


####################################
# Sidebar Filters (All Filters Here)
####################################


st.sidebar.header("Filters")

#####################################################
# Category Filters
#####################################################

selected_month = st.sidebar.multiselect(
    "Select Month",
    options=df["MONTH"].unique(),
    default=df["MONTH"].unique()
)

selected_store = st.sidebar.multiselect(
    "Select Store",
    options=df["STORE"].unique(),
    default=df["STORE"].unique()
)

selected_revenue_cohort = st.sidebar.multiselect(
    "Revenue Cohort",
    options=df["REVENUE COHORT"].unique(),
    default=df["REVENUE COHORT"].unique()
)

selected_ebitda_category = st.sidebar.multiselect(
    "EBITDA Category",
    options=df["EBITDA CATEGORY"].unique(),
    default=df["EBITDA CATEGORY"].unique()
)

selected_CM_cohort = st.sidebar.multiselect(
    "CM Cohort",
    options=df["CM COHORT"].unique(),
    default=df["CM COHORT"].unique()
)

selected_EBITDA_cohort = st.sidebar.multiselect(
    "EBITDA Cohort",
    options=df["EBITDA COHORT"].unique(),
    default=df["EBITDA COHORT"].unique()
)

#####################################################
# Range Filters
#####################################################
min_ebitda = float(df["KITCHEN EBITDA"].min())
max_ebitda = float(df["KITCHEN EBITDA"].max())

selected_ebitda = st.sidebar.slider(
    "EBITDA Range",
    min_ebitda,
    max_ebitda,
    (min_ebitda, max_ebitda)
)

min_GM = float(df["GROSS MARGIN"].min())
max_GM = float(df["GROSS MARGIN"].max())

selected_GM = st.sidebar.slider(
    "GROSS MARGIN (GM) Range",
    min_GM,
    max_GM,
    (min_GM, max_GM)
)

min_GM_PERCENT = float(df["GM_PERCENT"].min())
max_GM_PERCENT = float(df["GM_PERCENT"].max())

selected_GM_PERCENT = st.sidebar.slider(
    "GM% Range",
    min_GM_PERCENT,
    max_GM_PERCENT,
    (min_GM_PERCENT, max_GM_PERCENT)
)

min_NET_REVENUE = float(df["NET REVENUE"].min())
max_NET_REVENUE = float(df["NET REVENUE"].max())

selected_NET_REVENUE = st.sidebar.slider(
    "NET REVENUE Range",
    min_NET_REVENUE,
    max_NET_REVENUE,
    (min_NET_REVENUE, max_NET_REVENUE)
)


####################################
# Apply Filters
####################################

filtered_df = df[
    (df["MONTH"].isin(selected_month)) &
    (df["STORE"].isin(selected_store)) &
    (df["REVENUE COHORT"].isin(selected_revenue_cohort)) &
    (df["EBITDA CATEGORY"].isin(selected_ebitda_category)) &
    (df["CM COHORT"].isin(selected_CM_cohort)) &
    (df["EBITDA COHORT"].isin(selected_EBITDA_cohort)) & 
    (df["KITCHEN EBITDA"] >= selected_ebitda[0]) & (df["KITCHEN EBITDA"] <= selected_ebitda[1]) & 
    (df["GROSS MARGIN"] >= selected_GM[0]) & (df["GROSS MARGIN"] <= selected_GM[1]) &
    (df["GM_PERCENT"] >= selected_GM_PERCENT[0]) & (df["GM_PERCENT"] <= selected_GM_PERCENT[1]) &
    (df["NET REVENUE"] >= selected_NET_REVENUE[0]) & (df["NET REVENUE"] <= selected_NET_REVENUE[1])
]


####################################
# KPI Section
####################################

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Revenue ( ₹ )",
        f"{filtered_df['NET REVENUE'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Total EBITDA ( ₹ )",
        f"{filtered_df['KITCHEN EBITDA'].sum():,.2f}"
    )

with col3:
    st.metric(
        "Total Orders",
        f"{filtered_df['ORDER COUNT'].sum():,.0f}"
    )

with col4:
    st.metric(
        "Store Count",
        filtered_df["STORE"].nunique()
    )


####################################
# PNL TABLE
####################################

st.subheader("Kitchen Level PNL Table")

display_columns = [
    "MONTH",
    "CITY",
    "STORE",
    "NET REVENUE",
    "GROSS MARGIN",
    "GM_PERCENT",
    "KITCHEN EBITDA",
    "EBITDA_PERCENT",
    "VARIANCE"
]

st.dataframe(filtered_df[display_columns])


####################################
# CHARTS
####################################

st.subheader("Revenue by Store")

revenue_store = (
    filtered_df
    .groupby("STORE")["NET REVENUE"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    revenue_store,
    x="STORE",
    y="NET REVENUE",
    color="NET REVENUE"
)

st.plotly_chart(fig1, use_container_width=True)


st.subheader("Monthly EBITDA Trend")

monthly_ebitda = (
    filtered_df
    .groupby("MONTH")["KITCHEN EBITDA"]
    .sum()
    .reset_index()
)

fig2 = px.line(
    monthly_ebitda,
    x="MONTH",
    y="KITCHEN EBITDA",
    markers=True
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Revenue Contribution by City")

city_revenue = (
    filtered_df
    .groupby("CITY")["NET REVENUE"]
    .sum()
    .reset_index()
)

fig3 = px.pie(
    city_revenue,
    names="CITY",
    values="NET REVENUE",
    hole= 0.4
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Revenue vs EBITDA Analysis")

fig4 = px.scatter(
    filtered_df,
    x="NET REVENUE",
    y="KITCHEN EBITDA",
    color="CITY",
    size="ORDER COUNT",
    hover_data=["STORE"]
)

st.plotly_chart(fig4, use_container_width=True)







# CSV download
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data (CSV)",
    data=csv,
    file_name='filtered_kitchen_data.csv',
    mime='text/csv'
)

# Excel download
output = BytesIO()

with pd.ExcelWriter(output, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Data')

xlsx_data = output.getvalue()

st.download_button(
    label="Download Filtered Data (Excel)",
    data=xlsx_data,
    file_name='filtered_kitchen_data.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
