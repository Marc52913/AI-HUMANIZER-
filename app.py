import streamlit as st

st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️"
)

# Dark green theme
st.markdown("""
<style>
    .stApp {
        background-color: #0b2e1b;
        color: white;
    }

    h1 {
        color: #7CFC9A;
    }

    .stTextArea textarea {
        background-color: #143d26;
        color: white;
        border: 1px solid #2e6b45;
    }

    .stButton > button {
        background-color: #145a32;
        color: white;
        border: 1px solid #4caf70;
        border-radius: 8px;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #1b7a43;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("✍️ AI Text Humanizer")
st.write("Enter your text below.")

text = st.text_area(
    "Enter your text:",
    height=250,
    placeholder="Type or paste your text here..."
)

if text.strip():
    st.write(f"**Word count:** {len(text.split())}")

if st.button("✨ Humanize Text", type="primary"):
    if text.strip():
        st.success("Text is ready to be humanized!")

        st.text_area(
            "Humanized Text:",
            value=text,
            height=250
        )
    else:
        st.warning("Please enter some text first.")
