import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import warnings
from datetime import datetime

# Ignore warnings for cleaner output
warnings.filterwarnings("ignore")

# ==============================================================================
# PAGE SETUP
# ==============================================================================
st.set_page_config(
    page_title="PhonePe Dashboard",
    page_icon="📱",
    layout="wide"
)

# Add simple custom styling
st.markdown("""
<style>
    .main-header {
        background-color: #5B2C6F;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-box {
        background-color: #F4F6F7;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #5B2C6F;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE CONNECTION
# ==============================================================================
@st.cache_resource
def connect_to_database():
    """Create a connection to MySQL database"""
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="phone_pe",
            autocommit=True
        )
        return connection
    except Exception as e:
        st.error(f"❌ Cannot connect to database: {e}")
        st.stop()

def run_query(sql_query):
    """Run a SQL query and return results as DataFrame"""
    try:
        conn = connect_to_database()
        df = pd.read_sql(sql_query, conn)
        return df
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        return pd.DataFrame()

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h1>📱 PhonePe Transaction Dashboard</h1>
    <p>Simple analytics for digital payments across India</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR FILTERS
# ==============================================================================
st.sidebar.header("🔍 Filters")

# Get available years from database
years_query = "SELECT DISTINCT year FROM aggregated_transactions ORDER BY year DESC"
years_df = run_query(years_query)

if not years_df.empty:
    year_list = years_df['year'].tolist()
    selected_year = st.sidebar.selectbox("📅 Select Year", year_list)
else:
    st.error("No data available in database")
    st.stop()

# Get available states
states_query = "SELECT DISTINCT state FROM aggregated_transactions ORDER BY state"
states_df = run_query(states_query)
state_list = ["All States"] + states_df['state'].tolist()
selected_state = st.sidebar.selectbox("📍 Select State", state_list)

# Quarter selection
quarter_options = ["All Quarters", "Q1", "Q2", "Q3", "Q4"]
selected_quarter = st.sidebar.selectbox("📊 Select Quarter", quarter_options)

# Transaction type selection
types_query = "SELECT DISTINCT transaction_type FROM aggregated_transactions"
types_df = run_query(types_query)
type_list = ["All Types"] + types_df['transaction_type'].tolist()
selected_type = st.sidebar.selectbox("💳 Transaction Type", type_list)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def format_amount(amount):
    """Format large numbers for display"""
    if amount >= 1_000_000_000:
        return f"₹{amount/1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"₹{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"₹{amount/1_000:.1f}K"
    else:
        return f"₹{amount:.0f}"

def format_count(count):
    """Format counts for display"""
    if count >= 1_000_000_000:
        return f"{count/1_000_000_000:.1f}B"
    elif count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    else:
        return f"{count:.0f}"

# ==============================================================================
# BUILD SQL WHERE CLAUSE BASED ON FILTERS
# ==============================================================================
def build_where_clause(year, state, quarter, txn_type, table_name="aggregated_transactions"):
    """Build WHERE clause for SQL queries based on selected filters"""
    conditions = [f"year = {year}"]
    
    if state != "All States":
        conditions.append(f"state = '{state}'")
    
    if quarter != "All Quarters":
        quarter_num = quarter.replace("Q", "")
        conditions.append(f"quarter = {quarter_num}")
    
    if txn_type != "All Types" and table_name == "aggregated_transactions":
        conditions.append(f"transaction_type = '{txn_type}'")
    
    return " AND ".join(conditions)

# ==============================================================================
# KEY METRICS SECTION
# ==============================================================================
st.markdown("## 📊 Key Metrics")

# Build WHERE clause for queries
where_clause = build_where_clause(selected_year, selected_state, selected_quarter, selected_type)

# Get transaction metrics
txn_metrics_query = f"""
    SELECT 
        SUM(transaction_count) as total_transactions,
        SUM(transaction_amount) as total_amount,
        AVG(transaction_amount/transaction_count) as avg_transaction_value
    FROM aggregated_transactions 
    WHERE {where_clause}
"""
txn_metrics = run_query(txn_metrics_query)

# Get user metrics
user_where = build_where_clause(selected_year, selected_state, selected_quarter, selected_type, "map_users")
user_metrics_query = f"""
    SELECT 
        SUM(registered_users) as total_users,
        SUM(app_opens) as total_app_opens
    FROM map_users 
    WHERE {user_where}
"""
user_metrics = run_query(user_metrics_query)

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    if not txn_metrics.empty and txn_metrics['total_transactions'].iloc[0]:
        total_txn = txn_metrics['total_transactions'].iloc[0]
        st.metric("💳 Total Transactions", format_count(total_txn))
    else:
        st.metric("💳 Total Transactions", "0")

with col2:
    if not txn_metrics.empty and txn_metrics['total_amount'].iloc[0]:
        total_amt = txn_metrics['total_amount'].iloc[0]
        st.metric("💰 Total Amount", format_amount(total_amt))
    else:
        st.metric("💰 Total Amount", "₹0")

with col3:
    if not user_metrics.empty and user_metrics['total_users'].iloc[0]:
        total_users = user_metrics['total_users'].iloc[0]
        st.metric("👥 Registered Users", format_count(total_users))
    else:
        st.metric("👥 Registered Users", "0")

with col4:
    if not txn_metrics.empty and txn_metrics['avg_transaction_value'].iloc[0]:
        avg_value = txn_metrics['avg_transaction_value'].iloc[0]
        st.metric("📈 Avg Transaction", format_amount(avg_value))
    else:
        st.metric("📈 Avg Transaction", "₹0")

# ==============================================================================
# MAIN CONTENT - TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Transactions", "👥 Users", "🛡️ Insurance", "📋 Data Tables"])

# ------------------------------------------------------------------------------
# TAB 1: TRANSACTIONS
# ------------------------------------------------------------------------------
with tab1:
    st.header("Transaction Analysis")
    
    # Query for quarterly trends
    quarterly_query = f"""
        SELECT 
            quarter,
            SUM(transaction_count) as transactions,
            SUM(transaction_amount) as amount
        FROM aggregated_transactions 
        WHERE {where_clause}
        GROUP BY quarter
        ORDER BY quarter
    """
    quarterly_data = run_query(quarterly_query)
    
    if not quarterly_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Line chart for transaction count
            fig1 = px.line(
                quarterly_data, 
                x='quarter', 
                y='transactions',
                title="Transaction Count by Quarter",
                markers=True
            )
            fig1.update_xaxes(title="Quarter")
            fig1.update_yaxes(title="Number of Transactions")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Bar chart for transaction amount
            fig2 = px.bar(
                quarterly_data,
                x='quarter',
                y='amount',
                title="Transaction Amount by Quarter",
                color='amount'
            )
            fig2.update_xaxes(title="Quarter")
            fig2.update_yaxes(title="Amount (₹)")
            st.plotly_chart(fig2, use_container_width=True)
    
    # Transaction types breakdown
    st.subheader("Transaction Types")
    
    type_query = f"""
        SELECT 
            transaction_type,
            SUM(transaction_count) as count,
            SUM(transaction_amount) as amount
        FROM aggregated_transactions 
        WHERE year = {selected_year}
        GROUP BY transaction_type
        ORDER BY count DESC
    """
    type_data = run_query(type_query)
    
    if not type_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for transaction types
            fig3 = px.pie(
                type_data,
                values='count',
                names='transaction_type',
                title="Transaction Distribution by Type"
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Bar chart for amounts by type
            fig4 = px.bar(
                type_data,
                x='transaction_type',
                y='amount',
                title="Amount by Transaction Type"
            )
            fig4.update_xaxes(tickangle=45)
            st.plotly_chart(fig4, use_container_width=True)
    
    # Top states
    st.subheader("Top 10 States")
    
    states_query = f"""
        SELECT 
            state,
            SUM(transaction_count) as transactions,
            SUM(transaction_amount) as amount
        FROM aggregated_transactions 
        WHERE year = {selected_year}
        GROUP BY state
        ORDER BY transactions DESC
        LIMIT 10
    """
    states_data = run_query(states_query)
    
    if not states_data.empty:
        fig5 = px.bar(
            states_data,
            x='state',
            y='transactions',
            title="Top 10 States by Transaction Count",
            color='transactions'
        )
        fig5.update_xaxes(tickangle=45)
        st.plotly_chart(fig5, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: USERS
# ------------------------------------------------------------------------------
with tab2:
    st.header("User Analysis")
    
    # User growth by state
    user_state_query = f"""
        SELECT 
            state,
            SUM(registered_users) as users,
            SUM(app_opens) as app_opens
        FROM map_users 
        WHERE year = {selected_year}
        GROUP BY state
        ORDER BY users DESC
        LIMIT 15
    """
    user_state_data = run_query(user_state_query)
    
    if not user_state_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for users by state
            fig6 = px.bar(
                user_state_data,
                x='state',
                y='users',
                title="Top States by User Count",
                color='users'
            )
            fig6.update_xaxes(tickangle=45)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Scatter plot for engagement
            fig7 = px.scatter(
                user_state_data,
                x='users',
                y='app_opens',
                hover_data=['state'],
                title="User Engagement (App Opens vs Users)",
                size='app_opens'
            )
            st.plotly_chart(fig7, use_container_width=True)
    
    # Device brands
    st.subheader("Popular Device Brands")
    
    device_query = f"""
        SELECT 
            device_brand,
            SUM(device_count) as count
        FROM aggregated_users 
        WHERE year = {selected_year}
        GROUP BY device_brand
        ORDER BY count DESC
        LIMIT 10
    """
    device_data = run_query(device_query)
    
    if not device_data.empty:
        fig8 = px.bar(
            device_data,
            x='device_brand',
            y='count',
            title="Top 10 Device Brands",
            color='count'
        )
        fig8.update_xaxes(tickangle=45)
        st.plotly_chart(fig8, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: INSURANCE
# ------------------------------------------------------------------------------
with tab3:
    st.header("Insurance Analysis")
    
    # Insurance metrics
    insurance_query = f"""
        SELECT 
            state,
            SUM(insurance_count) as policies,
            SUM(insurance_amount) as amount
        FROM aggregated_insurances 
        WHERE year = {selected_year}
        GROUP BY state
        ORDER BY policies DESC
        LIMIT 10
    """
    insurance_data = run_query(insurance_query)
    
    if not insurance_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for insurance policies
            fig9 = px.bar(
                insurance_data,
                x='state',
                y='policies',
                title="Top States by Insurance Policies",
                color='policies'
            )
            fig9.update_xaxes(tickangle=45)
            st.plotly_chart(fig9, use_container_width=True)
        
        with col2:
            # Bar chart for insurance amount
            fig10 = px.bar(
                insurance_data,
                x='state',
                y='amount',
                title="Insurance Amount by State",
                color='amount'
            )
            fig10.update_xaxes(tickangle=45)
            st.plotly_chart(fig10, use_container_width=True)
    
    # Quarterly insurance trends
    insurance_quarterly_query = f"""
        SELECT 
            quarter,
            SUM(insurance_count) as policies,
            SUM(insurance_amount) as amount
        FROM aggregated_insurances 
        WHERE year = {selected_year}
        GROUP BY quarter
        ORDER BY quarter
    """
    insurance_quarterly = run_query(insurance_quarterly_query)
    
    if not insurance_quarterly.empty:
        fig11 = px.line(
            insurance_quarterly,
            x='quarter',
            y='policies',
            title="Insurance Policies by Quarter",
            markers=True
        )
        fig11.update_xaxes(title="Quarter")
        fig11.update_yaxes(title="Number of Policies")
        st.plotly_chart(fig11, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: DATA TABLES
# ------------------------------------------------------------------------------
with tab4:
    st.header("Raw Data Tables")
    
    # Show sample data from transactions
    st.subheader("Transaction Data Sample")
    sample_txn_query = f"""
        SELECT * FROM aggregated_transactions 
        WHERE year = {selected_year}
        LIMIT 50
    """
    sample_txn = run_query(sample_txn_query)
    
    if not sample_txn.empty:
        st.dataframe(sample_txn)
    
    # Show sample data from users
    st.subheader("User Data Sample")
    sample_user_query = f"""
        SELECT * FROM map_users 
        WHERE year = {selected_year}
        LIMIT 50
    """
    sample_user = run_query(sample_user_query)
    
    if not sample_user.empty:
        st.dataframe(sample_user)
    
    # Show sample data from insurance
    st.subheader("Insurance Data Sample")
    sample_insurance_query = f"""
        SELECT * FROM aggregated_insurances 
        WHERE year = {selected_year}
        LIMIT 50
    """
    sample_insurance = run_query(sample_insurance_query)
    
    if not sample_insurance.empty:
        st.dataframe(sample_insurance)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background-color: #F4F6F7; border-radius: 10px;">
    <h4>📱 PhonePe Dashboard</h4>
    <p>Data Source: PhonePe Pulse | Last Updated: {}</p>
    <p>Built with Streamlit, MySQL, and Plotly</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
