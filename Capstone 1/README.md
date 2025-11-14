# Data Insights App

A simple Streamlit application that connects to a SQLite database and uses the OpenAI API to generate insights, execute SQL queries, and analyze data through an LLM-powered agent.

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/...
cd your-repo

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Environment Variables

### Create a file named .env in the project root and add:

```bash
OPENAI_API_KEY=
GITHUB_TOKEN=
GITHUB_REPO=
```


▶️ Run the Application
```bash
streamlit run app.py
```
