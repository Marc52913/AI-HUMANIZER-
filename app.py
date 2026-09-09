import streamlit as st
import re
import random

st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️",
    layout="centered"
)

# -----------------------------
# PAGE DESIGN
# -----------------------------
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

.stButton > button:hover {
    background-color: #1b7a43;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SKSU LOGO
# -----------------------------
st.markdown("""
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("✍️ AI Text Humanizer")

st.markdown(
    '<p class="subtitle">Enter your text below and refine it.</p>',
    unsafe_allow_html=True
)

# -----------------------------
# TEXT INPUT
# -----------------------------
text = st.text_area(
    "Enter your text:",
    height=250,
    placeholder="Type or paste your text here..."
)

if text.strip():
    st.write(f"**Word count:** {len(text.split())}")


# -----------------------------
# SIMPLE TEXT REFINEMENT
# -----------------------------
def refine_text(text):
    """Refine text for clarity, grammar, and natural academic style."""

    replacements = {
        "don't": "do not",
        "doesn't": "does not",
        "can't": "cannot",
        "won't": "will not",
        "it's": "it is",
        "I'm": "I am",
        "I've": "I have",
        "you're": "you are",
        "they're": "they are",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not"
    }

    result = text

    # Expand common contractions
    for old, new in replacements.items():
        result = re.sub(
            r"\b" + re.escape(old) + r"\b",
            new,
            result,
            flags=re.IGNORECASE
        )

    # Clean unnecessary spaces
    result = re.sub(r"\s+", " ", result).strip()

    # Add spacing after punctuation when missing
    result = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", result)

    # Capitalize first character
    if result:
        result = result[0].upper() + result[1:]

    return result


# -----------------------------
# HUMANIZE BUTTON
# -----------------------------
if st.button("✨ Humanize Text", type="primary"):

    if not text.strip():
        st.warning("Please enter some text first.")

    else:
        with st.spinner("Processing your text..."):

            output_text = refine_text(text)

        st.success("Text processed successfully!")

        st.subheader("Refined Text")

        st.text_area(
            "Output:",
            value=output_text,
            height=250
        )

        st.write(
            f"**Output word count:** {len(output_text.split())}"
        )
