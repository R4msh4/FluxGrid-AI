import os
import json
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

def transcribe_audio(audio_file, api_key):
    """Convert recorded audio into text."""
    client = genai.Client(api_key=api_key)

    audio_bytes = audio_file.getvalue()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp.write(audio_bytes)
        temp_path = temp.name

    try:
        uploaded_audio = client.files.upload(file=temp_path)

        result = client.interactions.create(
            model="gemini-3.5-transcribe",
            input=[
                {
                    "type": "audio",
                    "uri": uploaded_audio.uri,
                    "mime_type": "audio/wav",
                }
            ],
        )

        return (result.output_text or "").strip()

    finally:
        os.unlink(temp_path)


st.set_page_config(
    page_title="FluxGrid AI",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 FluxGrid AI")
st.subheader("Community and Environmental Data Intelligence")
st.write(
    "Upload a CSV, explore any columns, visualize patterns, "
    "and ask questions about your data."
)

# ---------------- LOAD DATA ----------------

st.sidebar.header("📂 Upload Your Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload any CSV file",
    type=["csv"]
)


def load_csv(file):
    try:
        frame = pd.read_csv(file)

        if frame.empty:
            st.error("The CSV has no data rows.")
            st.stop()

        frame.columns = [str(c).strip() for c in frame.columns]

        # Remove unnamed and completely empty columns
        frame = frame.loc[
            :,
            [
                c for c in frame.columns
                if c and not c.lower().startswith("unnamed:")
            ]
        ]

        frame = frame.dropna(how="all").dropna(axis=1, how="all")

        if frame.empty or len(frame.columns) == 0:
            st.error("No usable data was found in this CSV.")
            st.stop()

        # Automatically detect columns containing mostly numbers
        for col in frame.columns:
            if frame[col].dtype == "object":
                raw = frame[col].astype("string").str.strip()

                cleaned = raw.str.replace(
                    r"[$£€₹,\s%]", "", regex=True
                )

                converted = pd.to_numeric(
                    cleaned, errors="coerce"
                )

                nonblank = raw.notna() & raw.ne("")

                if (
                    nonblank.sum() > 0
                    and converted[nonblank].notna().mean() >= 0.85
                ):
                    frame[col] = converted

        return frame

    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()


if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.success("CSV uploaded successfully.")
    st.caption(
        "Your uploaded dataset is being analyzed after basic cleanup."
    )

else:
    # Sample data shown before a CSV is uploaded
    df = pd.DataFrame({
        "building": [
            "Library", "Library",
            "Laboratory", "Laboratory",
            "Hostel", "Hostel"
        ],
        "month": [
            "2026-07", "2026-08",
            "2026-07", "2026-08",
            "2026-07", "2026-08"
        ],
        "electricity_kwh": [
            4200, 4500, 6800, 7200, 8000, 7600
        ]
    })

    st.info(
        "Showing sample electricity data. "
        "Upload any CSV to analyze your own dataset."
    )


# ---------------- DETECT COLUMN TYPES ----------------

for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        continue

    if any(
        token in str(col).lower()
        for token in ["date", "time", "month", "year", "day"]
    ):
        parsed = pd.to_datetime(df[col], errors="coerce")
        nonblank_count = df[col].notna().sum()

        if (
            nonblank_count
            and parsed.notna().sum()
            >= max(1, int(0.6 * nonblank_count))
        ):
            df[col] = parsed


numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

date_cols = df.select_dtypes(
    include=["datetime", "datetimetz"]
).columns.tolist()

categorical_cols = [
    c for c in df.columns
    if c not in numeric_cols and c not in date_cols
]


# ---------------- DATA OVERVIEW ----------------

st.header("📌 Dataset Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", f"{len(df.columns):,}")
m3.metric("Numeric columns", f"{len(numeric_cols):,}")
m4.metric(
    "Missing cells",
    f"{int(df.isna().sum().sum()):,}"
)

with st.expander("Preview dataset and column types", expanded=True):
    st.dataframe(df.head(100), use_container_width=True)

    type_info = pd.DataFrame({
        "Column": df.columns,
        "Detected type": [str(df[c].dtype) for c in df.columns],
        "Missing values": [
            int(df[c].isna().sum()) for c in df.columns
        ],
        "Unique values": [
            int(df[c].nunique(dropna=True)) for c in df.columns
        ]
    })

    st.dataframe(type_info, use_container_width=True)


# ---------------- EXPLORE NUMERIC COLUMNS ----------------

st.divider()
st.header("📊 Explore Any Column")

if numeric_cols:

    chosen_num = st.selectbox(
        "Choose a numeric column to analyze",
        numeric_cols
    )

    values = pd.to_numeric(
        df[chosen_num], errors="coerce"
    ).dropna()

    if not values.empty:

        a, b, c, d = st.columns(4)

        a.metric("Total / Sum", f"{values.sum():,.2f}")
        b.metric("Average", f"{values.mean():,.2f}")
        c.metric("Minimum", f"{values.min():,.2f}")
        d.metric("Maximum", f"{values.max():,.2f}")

        st.plotly_chart(
            px.histogram(
                df,
                x=chosen_num,
                title=f"Distribution of {chosen_num}"
            ),
            use_container_width=True
        )

    else:
        st.info("This column has no numeric values to summarize.")

    if categorical_cols:

        group_col = st.selectbox(
            "Optional: group this numeric column by a category",
            ["(No grouping)"] + categorical_cols
        )

        if group_col != "(No grouping)":

            grouped = (
                df.groupby(group_col, dropna=False)[chosen_num]
                .agg(["sum", "mean", "min", "max", "count"])
                .reset_index()
            )

            st.subheader(
                f"{chosen_num} grouped by {group_col}"
            )

            st.dataframe(grouped, use_container_width=True)

            st.plotly_chart(
                px.bar(
                    grouped,
                    x=group_col,
                    y="sum",
                    title=f"Total {chosen_num} by {group_col}"
                ),
                use_container_width=True
            )

else:
    st.info(
        "No numeric columns detected. You can still inspect "
        "the dataset and ask AI questions about it."
    )


# ---------------- CUSTOM CHART BUILDER ----------------

with st.expander("Build a custom chart"):

    chart_type = st.selectbox(
        "Chart type",
        ["Bar chart", "Line chart", "Scatter plot", "Box plot"]
    )

    x_col = st.selectbox(
        "X-axis / category",
        df.columns.tolist(),
        key="chart_x"
    )

    y_options = numeric_cols if numeric_cols else df.columns.tolist()

    y_col = st.selectbox(
        "Y-axis / value",
        y_options,
        key="chart_y"
    )

    color_col = st.selectbox(
        "Optional color grouping",
        ["(No color grouping)"] + categorical_cols
    )

    if st.button("Create chart"):

        try:
            kwargs = {
                "data_frame": df,
                "x": x_col,
                "y": y_col,
                "title": f"{y_col} by {x_col}"
            }

            if color_col != "(No color grouping)":
                kwargs["color"] = color_col

            if chart_type == "Bar chart":
                fig = px.bar(**kwargs)

            elif chart_type == "Line chart":
                fig = px.line(**kwargs, markers=True)

            elif chart_type == "Scatter plot":
                fig = px.scatter(**kwargs)

            else:
                fig = px.box(**kwargs)

            st.plotly_chart(fig, use_container_width=True)

        except Exception as exc:
            st.error(f"Could not create this chart: {exc}")


# ---------------- AI CHATBOT ----------------

st.divider()
st.header("🤖 Ask FluxGrid AI")

st.write(
    "Ask a question about any available column in your dataset."
)

with st.expander("API key setup help"):

    st.write(
        "Set GEMINI_API_KEY as an environment variable, "
        "or add it to Streamlit secrets."
    )

    st.code(
        'GEMINI_API_KEY = "your-key-here"',
        language="toml"
    )

    st.caption(
        "Keep your real API key private. "
        "Never upload your API key to GitHub."
    )



prompt = st.chat_input(
    "Type a question or tap the microphone...",
    accept_audio=True,
    audio_sample_rate=16000,
)


user_question = ""
audio_data = None

if isinstance(prompt, str):
    user_question = prompt.strip()

elif prompt is not None:
    user_question = (prompt.text or "").strip()
    audio_data = prompt.audio

if audio_data is not None:
    api_key = os.getenv("GEMINI_API_KEY", "")

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "") or api_key
    except Exception:
        pass 
    st.caption(f"API key loaded: {'Yes' if bool(api_key) else 'No'}")

    if not api_key:
        st.warning("API key not found. Please type your question.")
    else:
        try:
            with st.spinner("Converting your voice to text..."):
                user_question = transcribe_audio(audio_data, api_key)

            if user_question:
                st.caption(f"Recognized question: {user_question}")
            else:
                st.warning("No speech detected. Please try again.")

        except Exception as e:
            st.warning("Voice transcription failed. Please type your question.")
            st.caption(f"Technical detail: {e}")
            user_question = ""



if user_question:

    api_key = ""

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    if not api_key:

        st.error(
            "API key not found. Configure GEMINI_API_KEY "
            "in Streamlit secrets or your environment."
        )

    else:

        # Calculate summaries using Python for all dataset rows
        summaries = {}

        for col in numeric_cols:

            s = pd.to_numeric(
                df[col], errors="coerce"
            ).dropna()

            if not s.empty:

                summaries[col] = {
                    "count": int(s.count()),
                    "sum": float(s.sum()),
                    "mean": float(s.mean()),
                    "min": float(s.min()),
                    "max": float(s.max()),
                    "median": float(s.median())
                }

        # Summarize category columns
        category_values = {}

        for col in categorical_cols:

            category_values[col] = (
                df[col]
                .dropna()
                .astype(str)
                .value_counts()
                .head(30)
                .to_dict()
            )

        # Send a limited preview rather than the entire dataset
        preview = df.head(100).copy()
        preview = preview.astype(object).where(
            pd.notna(preview), None
        )

        payload = {
            "row_count": int(len(df)),
            "columns": [
                {
                    "name": str(c),
                    "dtype": str(df[c].dtype)
                }
                for c in df.columns
            ],
            "numeric_summaries": summaries,
            "categorical_value_counts_top_30": category_values,
            "data_preview_first_100_rows": preview.to_dict(
                orient="records"
            )
        }

        prompt = f"""
You are FluxGrid AI, a careful data analysis assistant.

Answer the user's question using the dataset evidence below.

Rules:
- Work with ANY column names present.
- Do not assume columns named building, month, or electricity_kwh.
- Use Python-computed summaries where applicable.
- Explain formulas for arithmetic questions.
- Do not invent units, columns, rows, or causal explanations.
- Distinguish correlation from causation.
- The preview contains at most 100 rows, but numeric summaries cover all rows.
- For calculations involving filters or multiple columns, only give an exact answer
  when the supplied evidence is sufficient.
- If evidence is insufficient, clearly explain the limitation.
- Keep answers clear and concise.

DATASET EVIDENCE (JSON):
{json.dumps(payload, ensure_ascii=False, default=str)}

USER QUESTION:
{user_question}
"""

        try:

            with st.spinner("FluxGrid AI is analyzing your data..."):

                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemma-4-26b-a4b-it",
                    contents=prompt
                )

            answer = getattr(response, "text", None)

            if answer:
                st.markdown("**FluxGrid AI's answer:**")
                st.write(answer)

            else:
                st.warning(
                    "The model returned no text. "
                    "Try a shorter question."
                )

        except Exception as exc:

            st.error(
                "The AI request failed. "
                "The detailed error is shown below."
            )

            st.code(f"{type(exc).__name__}: {exc}")


st.caption(
    "FluxGrid AI | Prototype | Verify findings against real data "
    "before making decisions."
)
