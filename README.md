🌱 FluxGrid AI

Community and Environmental Data Intelligence

FluxGrid AI is an AI-powered data analysis platform designed to help communities and institutions understand their environmental and resource-consumption data through interactive visualizations and natural-language questions.

🚀 Features

- 📂 CSV Data Upload: Upload your own dataset for analysis.
- 📊 Interactive Visualizations: Explore data through charts and visual summaries.
- 🤖 AI-Powered Data Q&A: Ask questions in natural language about the columns and values in your dataset.
- 🎤 Voice-Based Questions: Use microphone input to speak your questions instead of typing them.
- 🧮 Data Insights and Calculations: Explore consumption patterns, compare values, and request calculations based on your data.
- 🌍 Sustainability Focus: Identify resource-consumption patterns that can support more informed environmental decisions.

💡 Problem Statement

Environmental and utility data can be difficult to interpret without data-analysis skills. Communities and institutions need accessible ways to understand resource usage, identify unusual patterns, and make informed sustainability decisions.

💚 Our Solution

FluxGrid AI combines data visualization, AI-powered question answering, and voice input in one interface. Users can upload a dataset, explore its contents, and ask questions about the available data using everyday language or their voice.

🛠️ Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- Google GenAI SDK
- Google Gemini-family AI models

▶️ Run Locally

1. Clone or download this repository.

2. Install the required dependencies:
   
   pip install -r requirements.txt

3. Configure your "GEMINI_API_KEY" securely using an environment variable or Streamlit secrets.

4. Start the application:
   
   streamlit run app.py

🔐 API Key Security

Keep your API key private. Never commit your API key or ".streamlit/secrets.toml" file to GitHub.

⚠️ Limitations

FluxGrid AI is a prototype. Verify important findings and calculations against the original dataset before making real-world decisions. AI-generated interpretations may require independent validation.

🌿 Vision

Our vision is to make environmental data easier to understand and use, helping communities move toward more informed and sustainable resource management.

---

FluxGrid AI | Prototype | Verify findings against real data before making decisions.

Upload a CSV containing these columns to analyze electricity consumption.

📌 Project Status

Hackathon prototype. Validate AI-generated findings against the underlying data before making decisions.
