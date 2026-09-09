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
# DE-AI PHRASE MAPPINGS (neutralize AI-generated puffery)
# =========================================================

DEAI_PUFF = {
    r"\b(pivotal|crucial|vital|significant)\s+(role|moment|shift|turning\s*point)\b": "important role",
    r"\b(underscores|highlights|emphasizes)\s+(the\s+)?(importance|significance|enduring)\b": "shows",
    r"\b(stands?\s+as|serves?\s+as)\s+a\s+(testament|reminder)\b": "is",
    r"\breflects?\s+broader\b": "relates to",
    r"\b(showcases|demonstrates)\s+the\s+(rich|vibrant)\b": "has",
    r"\b(nestled|situated)\s+in\s+the\s+heart\b": "located in",
    r"\bboasts?\s+a\b": "has a",
    r"\b(landscape|tapestry)\s+of\b": "range of",
}

VAGUE_ATTRIB = {
    r"\b(experts?|scholars|researchers|critics)\s+(say|argue|claim|suggest)\b": "sources indicate",
    r"\b(it\s+is\s+widely\s+(accepted|believed|known))\b": "it is reported",
    r"\b(several\s+sources|many\s+publications)\b": "available sources",
}


# =========================================================
# AI TEXT STRUCTURAL REWRITER
# =========================================================

# Patterns specific to AI-generated text structure
AI_STRUCTURAL_PATTERNS = {
    # Overly formal sentence openings
    r"\b(It is noteworthy that|It is important to note that|It should be noted that)\b": "",
    
    # Redundant introductory phrases
    r"\b(In the context of|With respect to|In terms of)\b": "Regarding",
    
    # AI's favorite transition formula
    r"\b(Moreover|Furthermore|In addition),\s*(this|the|these)\s+": "",
    
    # Generic concluding statements
    r"\b(In conclusion|To summarize|Overall),\s*": "",
    
    # Passive voice triggers (convert to active where possible)
    r"\b(was|were)\s+(\w+ed)\s+by\b": r"\2",
    
    # Nominalization (turning verbs into nouns)
    r"\b(provide|offer)\s+(an?\s+)?(analysis|description|explanation)\s+of\b": r"analyze",
    r"\b(conduct|perform)\s+(an?\s+)?(assessment|evaluation)\s+of\b": r"assess",
    r"\b(make|give)\s+(an?\s+)?(argument|statement)\s+that\b": r"argue",
}

# AI overused phrases - replace with simpler alternatives
AI_PHRASE_REPLACEMENTS = {
    r"\bas\s+a\s+result\s+of\b": "because of",
    r"\bdue\s+to\s+the\s+fact\s+that\b": "because",
    r"\bin\s+order\s+to\b": "to",
    r"\bprior\s+to\b": "before",
    r"\bsubsequent\s+to\b": "after",
    r"\bin\s+the\s+event\s+that\b": "if",
    r"\bon\s+the\s+basis\s+of\b": "based on",
    r"\bwith\s+the\s+exception\s+of\b": "except",
    r"\bin\s+the\s+vicinity\s+of\b": "near",
    r"\bat\s+the\s+present\s+time\b": "currently",
    r"\bin\s+the\s+near\s+future\b": "soon",
    r"\bhas\s+the\s+ability\s+to\b": "can",
    r"\bhas\s+the\s+capacity\s+to\b": "can",
}

# Structural transformations
def break_ai_sentence_patterns(text):
    """Convert AI's typical long complex sentences into varied structures"""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if len(sentences) < 3:
        return text
    
    new_sentences = []
    for i, sent in enumerate(sentences):
        # Randomly split long sentences (>15 words) into two
        words = sent.split()
        if len(words) > 15 and random.random() < 0.3:
            mid = len(words) // 2
            # Find a natural break point (after a comma, conjunction, or preposition)
            break_points = [j for j in range(mid-3, mid+4) 
                          if 0 < j < len(words) and words[j][-1] in ',.;:']
            if break_points:
                split_idx = random.choice(break_points)
                first = " ".join(words[:split_idx+1])
                second = " ".join(words[split_idx+1:])
                # Capitalize second part
                if second:
                    second = second[0].upper() + second[1:]
                new_sentences.append(first)
                new_sentences.append(second)
            else:
                new_sentences.append(sent)
        else:
            new_sentences.append(sent)
    
    # Randomly combine some short sentences (<8 words)
    combined = []
    i = 0
    while i < len(new_sentences):
        if (i < len(new_sentences) - 1 and 
            len(new_sentences[i].split()) < 8 and 
            len(new_sentences[i+1].split()) < 8 and
            random.random() < 0.3):
            combined.append(new_sentences[i] + " " + new_sentences[i+1].lower())
            i += 2
        else:
            combined.append(new_sentences[i])
            i += 1
    
    return " ".join(combined)

def remove_redundant_modifiers(text):
    """Strip AI's excessive adjectives and adverbs"""
    # Remove redundant intensifiers
    intensifiers = r"\b(very|extremely|absolutely|completely|totally|utterly|highly|particularly|notably)\b"
    text = re.sub(intensifiers + r"\s+", "", text, flags=re.IGNORECASE)
    
    # Remove redundant "important" and "crucial" modifiers
    text = re.sub(r"\b(extremely|very)\s+(important|crucial)\b", r"\2", text, flags=re.IGNORECASE)
    
    return text

def simplify_ai_complexity(text):
    """Convert complex AI phrases to simpler human alternatives"""
    for pattern, replacement in AI_PHRASE_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def apply_ai_structural_fixes(text):
    """Apply all structural fixes to AI-generated text"""
    for pattern, replacement in AI_STRUCTURAL_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def humanize_ai_structure(text):
    """Comprehensive structural rewriting for AI text"""
    text = apply_ai_structural_fixes(text)
    text = simplify_ai_complexity(text)
    text = remove_redundant_modifiers(text)
    text = break_ai_sentence_patterns(text)
    return text


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
# EXPAND CONTRACTIONS (with human-like variation)
# =========================================================

def expand_contractions(text):
    for contraction, expanded in CONTRACTIONS.items():
        # 30% chance to skip expansion (human-like variation)
        if random.random() < 0.30:
            continue
        pattern = r"\b" + re.escape(contraction) + r"\b"
        text = re.sub(
            pattern,
            expanded,
            text,
            flags=re.IGNORECASE
        )
    return text


# =========================================================
# REPLACE COMMON WORDS (context-aware + probability gate)
# =========================================================

def replace_common_words(text):
    doc = nlp(text)
    words = text.split()
    new_words = []
    spacy_tokens = list(doc)
    token_idx = 0

    for word in words:
        token = spacy_tokens[token_idx] if token_idx < len(spacy_tokens) else None
        token_idx += 1

        punctuation = ""
        match = re.match(r"^([^A-Za-z]*)(.*?)([^A-Za-z]*)$", word)

        if not match:
            new_words.append(word)
            continue

        prefix = match.group(1)
        core = match.group(2)
        suffix = match.group(3)

        lower = core.lower()

        # Only replace if:
        # 1. word is in COMMON_REPLACEMENTS
        # 2. POS is NOUN, VERB, ADJ, ADV (not function words)
        # 3. random probability < 0.45 (human variation)
        if (lower in COMMON_REPLACEMENTS and token is not None and
            token.pos_ in {"NOUN", "VERB", "ADJ", "ADV"} and
            random.random() < 0.45):

            replacement = random.choice(COMMON_REPLACEMENTS[lower])

            if core[0].isupper():
                replacement = replacement.capitalize()

            core = replacement

        new_words.append(prefix + core + suffix)

    return " ".join(new_words)


# =========================================================
# ADD NATURAL TRANSITIONS (randomized, not fixed interval)
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

    if len(sentences) < 4:
        return text

    # choose random number of transitions (0 to min(2, len(sentences)-2))
    num_trans = random.randint(0, min(2, len(sentences)-2))
    positions = sorted(random.sample(range(1, len(sentences)-1), num_trans))

    output = []

    for idx, sentence in enumerate(sentences):
        if idx in positions:
            transition = random.choice(TRANSITIONS)
            if not any(sentence.startswith(t) for t in TRANSITIONS):
                sentence = transition + " " + sentence
        output.append(sentence)

    return " ".join(output)


# =========================================================
# DE-AI NEUTRALIZATION FUNCTIONS
# =========================================================

def neutralize_ai_puffery(text):
    for pattern, replacement in DEAI_PUFF.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def neutralize_vague_attribution(text):
    for pattern, replacement in VAGUE_ATTRIB.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


# =========================================================
# IMPROVE SENTENCE SPACING (with transition-aware capitalization)
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

    # Do not force uppercase if sentence starts with transition (e.g., "however,")
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned = []
    for sent in sentences:
        if sent and not any(sent.lower().startswith(t.lower() + " ") for t in TRANSITIONS):
            sent = sent[0].upper() + sent[1:] if len(sent) > 1 else sent.upper()
        cleaned.append(sent)

    return " ".join(cleaned)


# =========================================================
# MAIN REWRITING ENGINE
# =========================================================

def humanize_text(text):
    # Step 1: Structural fixes for AI-generated text (first pass)
    text = humanize_ai_structure(text)
    
    # Step 2: Expand contractions (with 30% skip)
    text = expand_contractions(text)
    
    # Step 3: Replace common words (context-aware, probability gate)
    text = replace_common_words(text)
    
    # Step 4: Add transitions (randomized)
    text = improve_transitions(text)
    
    # Step 5: Neutralize AI puffery
    text = neutralize_ai_puffery(text)
    
    # Step 6: Neutralize vague attribution
    text = neutralize_vague_attribution(text)
    
    # Step 7: Clean spacing and capitalization
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
