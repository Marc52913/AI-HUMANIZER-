import streamlit as st

st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️"
)

st.title("AI Text Humanizer")
st.write("Enter your text below.")

text = st.text_area(
    "Enter your text:",
    height=250,
    placeholder="Type or paste your text here..."
)

if text.strip():
    st.write(f"**Word count:** {len(text.split())}")
