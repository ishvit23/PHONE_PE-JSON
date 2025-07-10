"""
Streamlit Dashboard for PhonePe Transaction Insights
--------------------------------------------------
This dashboard visualizes PhonePe digital payments data across India, including transactions, users, and insurance metrics.
It provides interactive filters, summary metrics, and multiple business-focused charts.
"""
import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# 🌐 Database Connection
# -------------------------------
@st.cache_resource
def get_conn():
    """Establish and cache a connection to the MySQL database."""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="phone_pe"
    )

conn = get_conn()

# -------------------------------
# 📊 App Config & Title
# -------------------------------
st.set_page_config(page_title="PhonePe Transaction Insights", layout="wide")
st.title("📊 PhonePe Transaction Insights Dashboard")

# -------------------------------
# 📦 Sidebar Filters
# -------------------------------
# Fetch filter options from the database
years = pd.read_sql("SELECT DISTINCT year FROM aggregated_transactions ORDER BY year", conn)['year'].tolist()
states = pd.read_sql("SELECT DISTINCT state FROM aggregated_transactions ORDER BY state", conn)['state'].tolist()
transaction_types = pd.read_sql("SELECT DISTINCT transaction_type FROM aggregated_transactions", conn)['transaction_type'].tolist()

# Sidebar filter widgets
year = st.sidebar.selectbox("📅 Select Year", years, index=len(years) - 1)
state = st.sidebar.multiselect("🌍 Select State(s)", ["All"] + states, default=["All"])
transaction_type = st.sidebar.multiselect("💳 Select Transaction Type(s)", ["All"] + transaction_types, default=["All"])

# Reset filters button
if st.sidebar.button("Reset Filters"):
    year = years[-1]
    state = ["All"]
    transaction_type = ["All"]

# -------------------------------
# 📌 Metrics Summary
# -------------------------------
def get_metric_sum(table, col):
    """Return the sum of a column for the selected year from a given table."""
    result = pd.read_sql(f"SELECT SUM({col}) as total FROM {table} WHERE year={year}", conn)
    return result['total'][0] or 0

# Display key metrics at the top
col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Transactions", f"{get_metric_sum('aggregated_transactions', 'transaction_count'):,}")
col2.metric("👥 Registered Users", f"{get_metric_sum('aggregated_users', 'registered_users'):,}")
col3.metric("🛡️ Insurance Count", f"{get_metric_sum('aggregated_insurances', 'insurance_count'):,}")

# -------------------------------
# 🔍 Filtered Data
# -------------------------------
# Build SQL query based on sidebar filters
query = f"SELECT * FROM aggregated_transactions WHERE year={year}"
if "All" not in state:
    query += f" AND state IN ({','.join([repr(s) for s in state])})"
if "All" not in transaction_type:
    query += f" AND transaction_type IN ({','.join([repr(t) for t in transaction_type])})"
df = pd.read_sql(query, conn)

# -------------------------------
# 📊 Main Dashboard Tabs
# -------------------------------
# Create tabs for different business areas
# Tab 1: Transactions, Tab 2: Users & Devices, Tab 3: Insurance

tab1, tab2, tab3 = st.tabs(["Transactions", "Users & Devices", "Insurance"])

with tab1:
    st.subheader("📈 Transactions by Quarter")
    if not df.empty:
        # Barplot: Transaction count by quarter
        fig, ax = plt.subplots()
        sns.barplot(x="quarter", y="transaction_count", data=df, ax=ax)
        ax.set_ylabel("Transaction Count")
        ax.set_xlabel("Quarter")
        st.pyplot(fig)
    else:
        st.warning("No data found for selected filters.")

    st.subheader("💳 Transaction Amount by Type")
    # Aggregate transaction amount by type
    query2 = f"SELECT transaction_type, SUM(transaction_amount) as total_amount FROM aggregated_transactions WHERE year={year}"
    if "All" not in state:
        query2 += f" AND state IN ({','.join([repr(s) for s in state])})"
    query2 += " GROUP BY transaction_type"
    df2 = pd.read_sql(query2, conn)
    if not df2.empty:
        st.bar_chart(df2.set_index('transaction_type'))
    else:
        st.info("No transaction type data available.")

    st.subheader("🏆 Top 10 States by Transaction Amount")
    # Top 10 states by transaction amount
    df3 = pd.read_sql(f"""
        SELECT state, SUM(transaction_amount) as total_amount
        FROM aggregated_transactions
        WHERE year={year}
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 10
    """, conn)
    st.bar_chart(df3.set_index('state'))

with tab2:
    st.subheader("📱 Top Device Brands Among Users")
    # Top 10 device brands by user count
    df4 = pd.read_sql(f"""
        SELECT device_brand, SUM(device_count) as total_count
        FROM aggregated_users
        WHERE year={year}
        GROUP BY device_brand
        ORDER BY total_count DESC
        LIMIT 10
    """, conn)
    st.bar_chart(df4.set_index('device_brand'))

    st.subheader("📱 Top 10 States by App Opens")
    # Top 10 states by app opens
    df6 = pd.read_sql(f"""
        SELECT state, SUM(app_opens) as total_opens
        FROM map_users
        WHERE year={year}
        GROUP BY state
        ORDER BY total_opens DESC
        LIMIT 10
    """, conn)
    st.bar_chart(df6.set_index('state'))

with tab3:
    st.subheader("🛡️ Top 10 States by Insurance Transactions")
    # Top 10 states by insurance count
    df5 = pd.read_sql(f"""
        SELECT state, SUM(insurance_count) as total_count
        FROM aggregated_insurances
        WHERE year={year}
        GROUP BY state
        ORDER BY total_count DESC
        LIMIT 10
    """, conn)
    st.bar_chart(df5.set_index('state'))

# -------------------------------
# 💡 Insights & Recommendations
# -------------------------------
# Business insights and recommendations for stakeholders
st.markdown("""
---
### 💡 Insights & Recommendations

- 📈 **Transactions & Users**: Steady YoY growth confirms digital payment adoption.
- 💳 **Most-used transaction types**: Recharge and P2P are dominant.
- 📱 **Device usage**: Focus on Xiaomi, Samsung for scale; target Apple for engagement.
- 🛡️ **Insurance**: Concentrated in Tier 1 regions — expansion opportunity in underserved states.
- 📍 **App opens**: Analyze high-user but low-engagement states for re-targeting.

Use these findings to refine marketing, partner onboarding, and regional prioritization.
""")

# -------------------------------
# 📄 Footer/Attribution
# -------------------------------
# Attribution and data source
st.caption("Data Source: PhonePe Pulse | Dashboard by [Your Name]")
