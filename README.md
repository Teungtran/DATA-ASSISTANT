# DATA ANALYST ASSISSTANT 🤖💾

## Overview
This Streamlit-powered Assistant leverages Google's Generative AI to help developers and data professionals quickly generate SQL queries , Plots based on natural language descriptions.

## 🌟 Features
- Generate SQL queries from natural language inputs
- Support for multiple CSV/EXCEL file dialects
- Generate plots for simple visualization
- User-friendly Streamlit interface
- Powered by Google's advanced generative AI
- Query validation and optimization suggestions

## 🛠 Prerequisites
- Python 3.8+
- Streamlit
- Google Generative AI SDK
- Google Cloud API Key
- pandasai

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DATA-ASSISTANT.git
cd DATA-ASSISTANT
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Credentials
1. Create a Google Cloud project
2. Enable the Generative AI API
3. Create a service account and download the JSON key
4. Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## 🚀 Running the Application
```bash
streamlit run SQL.py
```

## 🔧 Configuration

### `config.yaml`
```yaml
database:
  supported_dialects:
    - MySQL
    - PostgreSQL
    - SQLite
    - Oracle
    - MSSQL
    .....

ai_settings:
  max_query_length: 500
  temperature: 0.7
  safety_threshold: moderate
```

## 📝 Usage Examples

### 1. Basic Query Generation
- Input: "Get all customers from New York"
- Output: 
  ```sql
  SELECT * FROM customers WHERE city = 'New York';
  ```

### 2. Complex Query Generation
- Input: "Find top 5 products by sales in the last quarter"
- Output:
  ```sql
  SELECT 
    product_id, 
    product_name, 
    SUM(sales_amount) as total_sales
  FROM sales
  WHERE sale_date BETWEEN '2023-10-01' AND '2023-12-31'
  GROUP BY product_id, product_name
  ORDER BY total_sales DESC
  LIMIT 5;
  ```


## 🛡️ Security
- Never commit API keys or sensitive credentials to the repository
- Use environment variables or secure secret management
- Implement input sanitization to prevent SQL injection

## 📊 Performance Metrics
- Average query generation time: < 2 seconds
- Support for 60+ SQL dialects per minute

## 📝 Usage Examples

### 1. Basic Query Generation
- Input: "Get all customers from New York"
- Output: 
  ```sql
  SELECT * FROM customers WHERE city = 'New York';
  ```

### 2. Complex Query Generation
- Input: "Find top 5 products by sales in the last quarter"
- Output:
  ```sql
  SELECT 
    product_id, 
    product_name, 
    SUM(sales_amount) as total_sales
  FROM sales
  WHERE sale_date BETWEEN '2023-10-01' AND '2023-12-31'
  GROUP BY product_id, product_name
  ORDER BY total_sales DESC
  LIMIT 5;
  ```


## 🛡️ Security
- Never commit API keys or sensitive credentials to the repository
- Use environment variables or secure secret management
- Implement input sanitization to prevent SQL injection

## 📊 Performance Metrics
- Average query generation time: < 2 seconds
- Support for 60+ SQL dialects per minute

## 🚧 Limitations
- Dependent on the quality and specificity of input description
- Requires basic understanding of database schema
- Do not have function to connect to your database  
- inflexibel plots ( only support Line, Bar, Hist plot, heatmap and pie chart)
- only support under 200mb input CSV/EXCEL file

## 🙏 Acknowledgments
- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://cloud.google.com/ai)
- Open-source community

---

**Disclaimer**: This tool is an AI assistant and should be used with careful review. Always validate generated SQL queries before execution.
