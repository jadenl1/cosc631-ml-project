import os
import streamlit as st
from src.app.predict import load_model, predict

st.set_page_config(page_title="Book Genre Predictor")
st.markdown(
    """
    <style>
        [data-testid="stToolbar"] {
            display: none;
        }
        .stApp, header[data-testid="stHeader"] {
            background-color: white;
            color: black;
        }
        html, body, [class*="st-"] {
            font-family: "Times New Roman", Times, serif;
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label {
            color: black;
            font-family: "Times New Roman", Times, serif;
        }
        .stTextArea textarea {
            background-color: white;
            color: black;
            border: 1px solid black;
            border-radius: 0;
            font-family: "Times New Roman", Times, serif;
        }
        .stButton button {
            background-color: white;
            color: black;
            border: 1px solid black;
            border-radius: 0;
            font-family: "Times New Roman", Times, serif;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Book Genre Predictor")
st.write("Enter a book summary to see the genres the model considers most likely.")


@st.cache_resource
def get_model():
    return load_model(os.environ.get("MODEL_PATH", "artifacts/model.joblib"))


summary = st.text_area(
    "Book summary", height=220, placeholder="Paste or type a book summary here..."
)
if st.button("Predict Genre"):
    if not summary.strip():
        st.warning("Please enter a book summary.")
    else:
        try:
            results = predict(get_model(), summary)
            st.subheader(f"Predicted genre: {results[0][0].title()}")
            st.write(f"Model-estimated probability: {results[0][1]:.1%}")
            st.write("**Top predicted genres**")
            for label, probability in results:
                st.write(f"{label.title()}: {probability:.1%}")
            st.caption(
                "These are model estimates, not guaranteed or calibrated confidence scores."
            )
        except Exception:
            st.error("Prediction is currently unavailable. Please try again later.")
