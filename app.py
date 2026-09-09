import streamlit as st

from transformer.app import (
    AcademicTextHumanizer,
    NLP_GLOBAL,
    download_nltk_resources
)

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
</style>
""", unsafe_allow_html=True)

# SKSU logo
st.markdown("""
<div class="logo">
    <img src="https://sksu.edu.ph/wp-content/uploads/2026/03/sksu_seal.png"
         width="120">
</div>
""", unsafe_allow_html=True)

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

if text.strip():
    st.write(f"**Word count:** {len(text.split())}")

# Humanize
if st.button("✨ Humanize Text", type="primary"):

    if not text.strip():
        st.warning("Please enter some text first.")

    else:
        with st.spinner("Processing your text..."):

            try:
                download_nltk_resources()

                humanizer = AcademicTextHumanizer(
                    p_passive=0.3,
                    p_synonym_replacement=0.3,
                    p_academic_transition=0.4
                )

                output_text = humanizer.humanize_text(
                    text,
                    use_passive=True,
                    use_synonyms=True
                )

                st.success("Text processed successfully!")

                st.subheader("Humanized Text")

                st.text_area(
                    "Output:",
                    value=output_text,
                    height=250
                )

                st.write(
                    f"**Output word count:** {len(output_text.split())}"
                )

            except Exception as e:
                st.error("Something went wrong while processing the text.")
                st.exception(e)
