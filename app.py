import streamlit as st

# Page settings
st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️",
    layout="centered"
)

# Dark green design
st.markdown("""
<style>
    .stApp {
        background-color: #0b2e1b;
        color: white;
    }

    .logo {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    h1 {
        color: #7CFC9A;
        text-align: center;
    }

    .subtitle {
        text-align: center;
        color: #d0e8d8;
        margin-bottom: 25px;
    }

    .stTextArea textarea {
        background-color: #143d26;
        color: white;
        border: 1px solid #2e6b45;
        border-radius: 8px;
    }

    .stButton > button {
        background-color: #145a32;
        color: white;
        border: 1px solid #4caf70;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #1b7a43;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# SKSU Logo
st.markdown("""
<div class="logo">
    <img src="https://sksu.edu.ph/wp-content/uploads/2026/03/sksu_seal.png"
         width="120">
</div>
""", unsafe_allow_html=True)

# Title
st.title("✍️ AI Text Humanizer")

st.markdown(
    '<p class="subtitle">Enter your text below and refine it.</p>',
    unsafe_allow_html=True
)

# Text input
text = st.text_area(
    "Enter your text:",
    height=250,
    placeholder="Type or paste your text here..."
)

# Word count
if text.strip():
    word_count = len(text.split())
    st.write(f"**Word count:** {word_count}")

# Humanize button
if st.button("✨ Humanize Text", type="primary"):
    if text.strip():
        st.success("Text is ready to be humanized!")

        st.text_area(
            "Humanized Text:",
            value=text,
            height=250
        )

        st.write(f"**Output word count:** {len(text.split())}")

    else:
        st.warning("Please enter some text first.")
