🌱 FluxGrid AI

AI-Powered Electricity Consumption Intelligence

FluxGrid AI is a Streamlit-based application that analyzes electricity consumption data to help communities identify usage patterns, compare buildings, and explore sustainability opportunities.

✨ Features

- 📂 Upload electricity data using CSV files.
- ⚡ Analyze electricity consumption by building and month.
- 📊 Visualize consumption using interactive charts.
- 🤖 Ask AI questions about electricity usage.
- 🌍 Explore potential energy-saving opportunities.

🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Google Gemini API

🚀 Getting Started

1. Install dependencies

python -m pip install -r requirements.txt

2. Configure the API key

Set your "GEMINI_API_KEY" environment variable locally, or configure it using your deployment platform's secrets settings.

Never upload your real API key to GitHub.

3. Run the application

python -m streamlit run app.py

📄 CSV Format

The current electricity analyzer expects these columns:

- "building"
- "month"
- "electricity_kwh"

Upload a CSV containing these columns to analyze electricity consumption.

🔐 Security

Do not commit API keys, passwords, or private datasets.

📌 Project Status

Hackathon prototype. Validate AI-generated findings against the underlying data before making decisions.
