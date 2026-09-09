import re
import random
import streamlit as st
import spacy
from nltk.corpus import wordnet
import nltk


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️",
    layout="centered"
)


# =========================================================
# LOAD NLP MODEL
# =========================================================

@st.cache_resource
def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error(
            "The spaCy English model is missing. "
            "Please add en_core_web_sm to requirements.txt."
        )
        st.stop()


nlp = load_nlp()


# =========================================================
# DOWNLOAD NLTK RESOURCES
# =========================================================

@st.cache_resource
def setup_nltk():

    resources = [
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4")
    ]

    for path, package in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


setup_nltk()


# =========================================================
# PAGE STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b2e1b;
    color: white;
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


# =========================================================
# TITLE
# =========================================================

st.title("✍️ AI Text Humanizer")

st.markdown(
    '<p class="subtitle">'
    'Rewrite your text for clearer and more natural academic writing.'
    '</p>',
    unsafe_allow_html=True
)


# =========================================================
# TEXT INPUT
# =========================================================

text = st.text_area(
    "Enter your text:",
    height=250,
    placeholder="Type or paste your text here..."
)


if text.strip():
    st.write(f"**Word count:** {len(text.split())}")


# =========================================================
# CONTRACTIONS
# =========================================================

CONTRACTIONS = {
    "don't": "do not",
    "doesn't": "does not",
    "can't": "cannot",
    "couldn't": "could not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "won't": "will not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "it's": "it is",
    "I'm": "I am",
    "I've": "I have",
    "I'll": "I will",
    "you're": "you are",
    "you've": "you have",
    "they're": "they are",
    "they've": "they have",
    "we're": "we are"
}


# =========================================================
# WORD REPLACEMENTS
# =========================================================

COMMON_REPLACEMENTS = {
    "important": [
        "significant",
        "essential",
        "valuable"
    ],

    "help": [
        "assist",
        "support",
        "aid"
    ],

    "use": [
        "utilize",
        "apply",
        "employ"
    ],

    "show": [
        "demonstrate",
        "illustrate",
        "indicate"
    ],

    "get": [
        "obtain",
        "receive",
        "gain"
    ],

    "good": [
        "effective",
        "beneficial",
        "positive"
    ],

    "bad": [
        "negative",
        "harmful",
        "unfavorable"
    ],

    "big": [
        "substantial",
        "considerable",
        "significant"
    ],

    "many": [
        "numerous",
        "several",
        "various"
    ],

    "make": [
        "create",
        "produce",
        "develop"
    ],

    "think": [
        "believe",
        "consider",
        "maintain"
    ]
}


# =========================================================
# SYNONYM FUNCTION
# =========================================================

def get_synonym(word):

    clean_word = re.sub(r"[^a-zA-Z]", "", word)

    if not clean_word:
        return word

    synsets = wordnet.synsets(clean_word)

    if not synsets:
        return word

    candidates = []

    for synset in synsets[:3]:
        for lemma in synset.lemmas():

            synonym = lemma.name().replace("_", " ")

            if (
                synonym.lower() != clean_word.lower()
                and synonym.isalpha()
            ):
                candidates.append(synonym)

    if not candidates:
        return word

    return random.choice(candidates)


# =========================================================
# EXPAND CONTRACTIONS
# =========================================================

def expand_contractions(text):

    for contraction, expanded in CONTRACTIONS.items():

        pattern = r"\b" + re.escape(contraction) + r"\b"

        text = re.sub(
            pattern,
            expanded,
            text,
            flags=re.IGNORECASE
        )

    return text


# =========================================================
# REPLACE COMMON WORDS
# =========================================================

def replace_common_words(text):

    words = text.split()

    new_words = []

    for word in words:

        punctuation = ""

        match = re.match(r"^([^A-Za-z]*)(.*?)([^A-Za-z]*)$", word)

        if match:

            prefix = match.group(1)
            core = match.group(2)
            suffix = match.group(3)

            lower = core.lower()

            if lower in COMMON_REPLACEMENTS:

                replacement = random.choice(
                    COMMON_REPLACEMENTS[lower]
                )

                if core[0].isupper():
                    replacement = replacement.capitalize()

                core = replacement

            new_words.append(
                prefix + core + suffix
            )

        else:
            new_words.append(word)

    return " ".join(new_words)


# =========================================================
# ADD NATURAL TRANSITIONS
# =========================================================

TRANSITIONS = [
    "Furthermore,",
    "Moreover,",
    "In addition,",
    "However,",
    "As a result,",
    "Therefore,"
]


def improve_transitions(text):

    doc = nlp(text)

    sentences = [
        sent.text.strip()
        for sent in doc.sents
        if sent.text.strip()
    ]

    if len(sentences) < 3:
        return text

    output = []

    for index, sentence in enumerate(sentences):

        if index > 0 and index % 3 == 0:

            transition = random.choice(TRANSITIONS)

            if not sentence.startswith(
                tuple(TRANSITIONS)
            ):
                sentence = transition + " " + sentence

        output.append(sentence)

    return " ".join(output)


# =========================================================
# IMPROVE SENTENCE SPACING
# =========================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    text = re.sub(
        r"([.!?])([A-Za-z])",
        r"\1 \2",
        text
    )

    if text:
        text = text[0].upper() + text[1:]

    return text


# =========================================================
# MAIN REWRITING ENGINE
# =========================================================

def humanize_text(text):

    # Step 1
    text = expand_contractions(text)

    # Step 2
    text = replace_common_words(text)

    # Step 3
    text = improve_transitions(text)

    # Step 4
    text = clean_text(text)

    return text


# =========================================================
# HUMANIZE BUTTON
# =========================================================

if st.button("✨ Humanize Text", type="primary"):

    if not text.strip():

        st.warning(
            "Please enter some text first."
        )

    else:

        with st.spinner(
            "Rewriting your text..."
        ):

            try:

                output_text = humanize_text(text)

                st.success(
                    "Text successfully rewritten!"
                )

                st.subheader(
                    "Rewritten Text"
                )

                st.text_area(
                    "Output:",
                    value=output_text,
                    height=300
                )

                st.write(
                    f"**Output word count:** "
                    f"{len(output_text.split())}"
                )

                st.download_button(
                    label="⬇️ Download Text",
                    data=output_text,
                    file_name="rewritten_text.txt",
                    mime="text/plain"
                )

            except Exception as e:

                st.error(
                    "Something went wrong while "
                    "rewriting the text."
                )

                st.exception(e)
