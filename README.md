# PhonePe Transaction Insights

## 📊 Project Overview
This project analyzes PhonePe’s digital payments data across India, focusing on transactions, users, and insurance. Using SQL, Python, and interactive dashboards, it uncovers key trends, regional patterns, and actionable business insights to support data-driven decision-making.

## 🗂️ Data Sources
- **PhonePe Pulse** open-source repository
- Aggregated, map-level, and top-N data in nested JSON format
- Covers all Indian states/UTs, multiple years, and transaction types

## 🚀 Features
- **Data Engineering:** Scripts to parse, clean, and load JSON data into a MySQL database
- **Exploratory Data Analysis (EDA):** Jupyter notebook with 15+ business-focused visualizations
- **Interactive Dashboard:** Streamlit app with dynamic filters, tabs, and actionable insights
- **Business Case Studies:** Real-world use cases and recommendations

## 🛠️ Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd PHONE_PE_INSIGHTS
   ```
2. **Install dependencies:**
   - Create and activate a virtual environment (optional)
   - Install required Python packages:
     ```bash
     pip install -r requirements.txt
     ```
3. **Set up MySQL database:**
   - Create a database named `phone_pe`
   - Run the SQL script in `SQL/create_all_tables.sql` to create tables
4. **Load data:**
   - Place PhonePe Pulse JSON data in the `data/` directory (see structure)
   - Run the scripts in the `scripts/` folder to populate the database

## 💻 Usage
### 1. Jupyter Notebook (EDA)
- Open the main notebook in `Notebooks/`
- Run cells to explore data, generate visualizations, and read insights

### 2. Streamlit Dashboard
- Run the dashboard app:
  ```bash
  streamlit run Streamlit_Dashboard/dashboard.py
  ```
- Use sidebar filters and tabs to explore transactions, users, and insurance data interactively

## 🔑 Key Insights
- Digital payments and user registrations are growing steadily across India
- Certain states lead in transaction volume and engagement; others show untapped potential
- Device usage patterns and insurance adoption reveal new business opportunities
- The dashboard enables real-time, business-focused exploration and decision-making

## 📞 Contact
For questions or collaboration, please contact: [Your Name] (<your-email@example.com>)

---
*Data Source: PhonePe Pulse | Project by [Your Name]* 