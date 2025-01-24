import pandas as pd
import streamlit as st
import spacy
import re
from spacy.cli import download  

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# page configuration
st.set_page_config(page_title="Financial Chatbot", layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def load_data():
    data = pd.read_csv("financial_data.csv")
    data["Revenue Growth (%)"] = data.groupby("Company")["Total Revenue ($B)"].pct_change() * 100
    data["Debt-to-Assets Ratio"] = (data["Total Liabilities ($B)"] / data["Total Assets ($B)"]) * 100
    data["ROA (%)"] = (data["Net Income ($B)"] / data["Total Assets ($B)"]) * 100
    data["Operating Margin (%)"] = (data["Net Income ($B)"] / data["Total Revenue ($B)"]) * 100
    data.fillna(0, inplace=True)
    return data

data = load_data()

# Mapping for metrics
metric_mapping = {
    "total revenue": "Total Revenue ($B)",
    "net income": "Net Income ($B)",
    "total assets": "Total Assets ($B)",
    "total liabilities": "Total Liabilities ($B)",
    "cash flow": "Cash Flow from Operating Activities ($B)",
    "revenue growth": "Revenue Growth (%)",
    "debt-to-assets ratio": "Debt-to-Assets Ratio",
    "return on assets": "ROA (%)",
    "operating margin": "Operating Margin (%)"
}

# Enhanced query response function
def get_response(query):
    year = None
    metric = None
    company = None

    # Extract year using regex
    year_match = re.search(r'\b(20\d{2})\b', query)
    if year_match:
        year = int(year_match.group(1))

    # Extract company name by matching against dataset
    company_list = data["Company"].unique()
    for comp in company_list:
        if comp.lower() in query.lower():
            company = comp
            break

    # Extract metric using the mapping
    for key, value in metric_mapping.items():
        if key in query.lower():
            metric = value
            break

    # Check if all components were successfully extracted
    if not company or not year or not metric:
        return "Sorry, I couldn't understand your query. Please ask about a specific company, year, and metric."

    # Filter the dataset to find the matching row
    filtered_data = data[
        (data["Company"].str.contains(company, case=False, na=False)) & 
        (data["Year"] == year)
    ]

    # Return result or error message if data is missing
    if not filtered_data.empty:
        result = filtered_data.iloc[0][metric]
        return f"The {metric.lower()} for {company.title()} in {year} is {result}."
    else:
        return f"Sorry, I couldn't find any data for {company.title()} in {year}."

# Streamlit app with dynamic styling
st.markdown(
    """
    <style>
    body {
        background-color: #f9f9f9;
        font-family: 'Poppins', sans-serif;
    }
    .main-title {
        background: linear-gradient(90deg, #007bff, #00c853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #007bff;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .info-box p {
        color: black;
        font-size: 16px;
    }
    .info-box ul {
        list-style-type: none;
        padding: 0;
    }
    .info-box li {
        font-size: 16px;
        margin: 5px 0;
    }
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #1e1e1e;
        }
        .info-box {
            background-color: #2e3a47;
        }
        .info-box p {
            color: #ffffff;
        }
        .info-box li {
            color: #ffffff;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Financial Chatbot</div>', unsafe_allow_html=True)
st.write("Explore financial metrics and trends with ease! Ask me anything about a company's performance.")

# Add a box to show supported companies
st.markdown(
    """
    <div class="info-box">
        <p>Currently, this chatbot provides financial insights for the following companies:</p>
        <ul>
            <li>Amazon</li>
            <li>Microsoft</li>
            <li>Apple</li>
            <li>Tesla</li>
        </ul>
        <p>Feel free to ask about their revenue, net income, assets, liabilities, and more!</p>
    </div>
    """, unsafe_allow_html=True)

# Input field for user query
query = st.text_input("Your Question:", placeholder="E.g., What is the total revenue for Apple in 2021?", key="query")

# Button to get response
if st.button("Get Response"):
    if query:
        response = get_response(query)
        st.success(response)
    else:
        st.warning("Please enter a query.")

# Visualize Trends
st.write("---")
st.markdown("## 📈 Visualize Trends")
company = st.selectbox("Select Company for Trends", data["Company"].unique())
metrics_to_visualize = st.multiselect("Select Metrics", metric_mapping.keys(), default=["total revenue"])
if company and metrics_to_visualize:
    filtered_data = data[data["Company"] == company]
    st.line_chart(filtered_data.set_index("Year")[[metric_mapping[m] for m in metrics_to_visualize]])

st.write("### 🔍 Sample Queries:")
st.markdown("""
- What is the total revenue for **Tesla** in 2023?  
- Show the operating margin for **Apple** in 2021.  
- What is the debt-to-assets ratio for **Microsoft** in 2020?  
- Tell me the net income of **Amazon** in 2022.  
""")
