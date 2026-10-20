import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

st.set_page_config(
    page_title="FluxGrid AI",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 FluxGrid AI")
st.subheader("Community and Environmental Data Intelligence")
st.write("Explore electricity consumption using data, charts, and AI.")

# Demo electricity dataset
data = {
    "building": [
        "Library", "Library", "Library",
        "Laboratory", "Laboratory", "Laboratory",
        "Hostel", "Hostel", "Hostel",
        "Academic Block", "Academic Block", "Academic Block",
        "Sports Complex", "Sports Complex", "Sports Complex"
    ],
    "month": [
        "2026-07", "2026-08", "2026-09",
        "2026-07", "2026-08", "2026-09",
        "2026-07", "2026-08", "2026-09",
        "2026-07", "2026-08", "2026-09",
        "2026-07", "2026-08", "2026-09"
    ],
    "electricity_kwh": [
        4200, 4500, 5100,
        6800, 7200, 9500,
        8000, 7600, 7400,
        5500, 5900, 6200,
        3000, 3400, 3200
    ]
}

# Upload a dataset or use the built-in demo data
st.sidebar.header("📂 Upload Your Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload an electricity CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "building",
            "month",
            "electricity_kwh"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            st.error(
                "CSV is missing required columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        df["month"] = pd.to_datetime(
            df["month"],
            errors="coerce"
        )
        df["electricity_kwh"] = pd.to_numeric(
            df["electricity_kwh"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["building", "month", "electricity_kwh"]
        )

        if df.empty:
            st.error("The CSV contains no valid data rows.")
            st.stop()

        if (df["electricity_kwh"] < 0).any():
            st.error("Electricity values cannot be negative.")
            st.stop()

        st.success("Your dataset was uploaded successfully!")

    except Exception as e:
        st.error(f"Could not read the CSV file: {e}")
        st.stop()

else:
    df = pd.DataFrame(data)
    df["month"] = pd.to_datetime(df["month"])

st.info(
    "Demo data only: these are synthetic figures, "
    "not actual campus measurements."
)

# Summary metrics
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Consumption",
    f"{df['electricity_kwh'].sum():,.0f} kWh"
)
col2.metric(
    "Average Record",
    f"{df['electricity_kwh'].mean():,.1f} kWh"
)
col3.metric("Buildings", df["building"].nunique())

st.divider()
st.header("Explore Your Data")

question = st.selectbox(
    "Choose a question",
    [
        "Which building consumed the most electricity?",
        "What is the total electricity consumption?",
        "How does consumption change over time?",
        "Compare electricity consumption between months?",
    ]
)

if question == "Which building consumed the most electricity?":
    totals = (
        df.groupby("building")["electricity_kwh"]
        .sum()
        .sort_values(ascending=False)
    )
    st.success(
        f"{totals.index[0]} consumed the most electricity: "
        f"{totals.iloc[0]:,.0f} kWh."
    )

    fig = px.bar(
        totals.reset_index(),
        x="building",
        y="electricity_kwh",
        title="Total Electricity Consumption by Building",
        labels={"electricity_kwh": "Consumption (kWh)"}
    )
    st.plotly_chart(fig, use_container_width=True)
elif question == "How does consumption change over time?":
    monthly = (
        df.groupby(["month", "building"])["electricity_kwh"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="month",
        y="electricity_kwh",
        color="building",
        markers=True,
        title="Consumption Trends by Building",
        labels={
            "month": "Month",
            "electricity_kwh": "Consumption (kWh)"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    monthly = (
        df.groupby("month")["electricity_kwh"]
        .sum()
        .sort_index()
    )
    st.subheader("Monthly Consumption Comparison")

    if len(monthly) < 2:
        st.warning(
            "At least two different months are needed "
            "to compare consumption."
        )
    else:
        comparison = monthly.diff().dropna()

        result = pd.DataFrame({
            "Total consumption (kWh)": monthly,
            "Change from previous month (kWh)": monthly.diff()
        })

        st.dataframe(result, use_container_width=True)

        first_month = monthly.index[0]
        last_month = monthly.index[-1]
        change = monthly.iloc[-1] - monthly.iloc[0]

        st.write(
            f"From {first_month:%B %Y} to {last_month:%B %Y}, "
            f"consumption changed by {change:,.0f} kWh."
        )

        fig = px.bar(
            monthly.reset_index(),
            x="month",
            y="electricity_kwh",
            title="Total Electricity Consumption by Month",
            labels={
                "month": "Month",
                "electricity_kwh": "Consumption (kWh)"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# AI chat assistant
st.divider()
st.header("🤖 Ask FluxGrid AI")
st.write(
    "Ask questions about electricity consumption, trends, "
    "or possible sustainability improvements."
)

user_question = st.chat_input(
    "Example: Why might laboratory electricity use be increasing?"
)

if user_question:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "API key not found. Set GEMINI_API_KEY in the terminal "
            "before starting FluxGrid AI."
        )
    else:
        try:
            client = genai.Client(api_key=api_key)

            # Calculate evidence using Python
            building_totals = (
                df.groupby("building")["electricity_kwh"]
                .sum()
                .sort_values(ascending=False)
            )
            monthly_totals = (
                df.groupby("month")["electricity_kwh"]
                .sum()
                .sort_index()
            )
            # Calculate change between the first and last month
            if len(monthly_totals) >= 2:
                first_total = monthly_totals.iloc[0]
                last_total = monthly_totals.iloc[-1]
                change = last_total - first_total

                if first_total != 0:
                    percentage_change = (
                        change / first_total
                    ) * 100
                else:
                    percentage_change = None
            else:
                first_total = None
                last_total = None
                change = None
                percentage_change = None

            evidence = f"""
            First month total: {first_total}
            Last month total: {last_total}
            Change between first and last month: {change} kWh
            Percentage change: { f"{percentage_change:.2f}%"
    if percentage_change is not None
    else "Not available"
}
            Total electricity consumption: {df['electricity_kwh'].sum()} kWh
            Average monthly building record:
            {df['electricity_kwh'].mean():.1f} kWh

            Consumption by building:
            {building_totals.to_string()}

            Total consumption by month:
            {monthly_totals.to_string()}

            Full dataset:
            {df.to_string(index=False)}
            """

            prompt = f"""
            You are FluxGrid AI, an environmental data assistant.

            Answer the user's question using only the evidence below.
            The dataset is synthetic demo data, not real campus data.

            Rules:
            - Use the supplied calculations and figures accurately.
            - Do not invent measurements or claim an unproven cause.
            - If suggesting causes, label them as possibilities to investigate.
            - Give practical, concise sustainability recommendations.
            - If the data cannot answer a question, explain what is missing.

            EVIDENCE:
            {evidence}

            USER QUESTION:
            {user_question}
            """

            with st.spinner("FluxGrid AI is analysing your data..."):
                response = client.models.generate_content(
                    model="gemma-4-26b-a4b-it",
                    contents=prompt
                )

            st.markdown("**FluxGrid AI's answer:**")
            st.write(response.text)

        except Exception as e:
            st.error(
                "The AI request failed. Check your internet connection, "
                "API access, model availability, and usage limits."
            )
            st.caption(f"Technical details: {e}")

st.caption(
    "FluxGrid AI | Prototype | Verify findings against real data "
    "before making decisions."
)
