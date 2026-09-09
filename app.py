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
# PATTERN LIBRARY – SOURCE: 4 EXTERNAL GUIDES
# =========================================================

# SOURCE 1: Hunting the Muse (https://huntingthemuse.net/library/how-to-tell-if-writing-is-ai)
# Patterns: em dashes (no spaces), forced sass, AI buzzwords
EM_DASH_PATTERNS = {
    r"(?<!\s)—(?!\s)": " — ",  # unspaced em dash → spaced
    r"—": " — ",                # catch any remaining
}

SASS_PHRASES = {
    r"\bBut here's the thing[:]\s*": "But ",
    r"\bThen I realized[:]\s*": "",
    r"\bThe result[?][:]\s*": "",
    r"\bHot take[:]\s*": "",
    r"\bAnd honestly[?][:]\s*": "",
}

AI_BUZZWORDS_HUNTING = {
    r"\bdelve\b": "explore",
    r"\btapestry\b": "range",
    r"\bnavigate\b": "handle",
    r"\bgrounded\b": "based",
    r"\bquietly\b": "",
    r"\bunlock\b": "reveal",
    r"\bempower\b": "enable",
    r"\belevate\b": "improve",
}

# SOURCE 2: AI Detector Checker (https://detector-checker.ai/blog/signs-of-ai-generated-text-vs-human-written-text/)
# Patterns: generic claims, uniform structure (handled in break_ai_sentence_patterns)
GENERIC_CLAIMS = {
    r"\b(increasingly|critically)\s+(significant|important|transformative)\b": r"\1 relevant",
    r"\bplays?\s+a\s+crucial\s+role\b": "helps",
    r"\b(it is|this is)\s+(widely\s+)?(considered|regarded)\s+as\s+(important|significant)\b": "it matters",
}

# SOURCE 3: Wandering Educators (https://www.wanderingeducators.com/best/stories/top-signs-writing-generated-by-ai-how-to-fix-it)
# Patterns: transition crutches, stock phrases, emotional flatline (handled via personal detail injection prompt)
TRANSITION_CRUTCHES = {
    r"\bMoreover,\s*": "",
    r"\bFurthermore,\s*": "",
    r"\bConsequently,\s*": "",
    r"\bIn addition,\s*": "",
    r"\bAdditionally,\s*": "",
}

STOCK_PHRASES = {
    r"\bit is important to note that\b": "",
    r"\bin today's fast-paced world\b": "Today",
    r"\bin the dynamic landscape of\b": "In",
    r"\bas the world continues to evolve\b": "",
    r"\bit goes without saying\b": "",
}

# SOURCE 4: Sean Kernan (https://seanjkernan.substack.com/p/13-signs-you-used-chatgpt-to-write)
# Patterns: parallelism, hedging, blogging clichés, buzzwords
PARALLELISM_PATTERNS = {
    r"\bIt's not about\s+([^,;.]+?),\s+it's about\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(1)} matters more than {m.group(2)}",
    r"\bIt's not just\s+([^,;.]+?),\s+it's also\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(1)} and {m.group(2)} both matter",
    r"\bNot only\s+([^,;.]+?),\s+but also\s+([^,;.]+?)\b":
        lambda m: f"{m.group(1)} and {m.group(2)}",
}

HEDGING_PHRASES = {
    r"\btypically\b": "often",
    r"\bmore often than not\b": "usually",
    r"\bmight be\b": "may be",
    r"\bdon't always\b": "sometimes don't",
    r"\bcan also\b": "also",
}

BLOG_CLICHES = {
    r"\bAh, yes,\s*": "",
    r"\byou have the power to\b": "you can",
    r"\bnow, this might make you wonder\b": "",
    r"\bwithout further ado\b": "",
    r"\bhave you ever wondered\b": "",
    r"\beveryone wants to\b": "Many want to",
    r"\bif you have ever wondered\b": "",
}

AI_BUZZWORDS_KERNAN = {
    r"\bleverage\b": "use",
    r"\bpivotal\b": "important",
    r"\bcomprehensive\b": "broad",
    r"\brobust\b": "strong",
}

# Combined buzzword dictionary (merge both sources)
AI_BUZZWORDS = {**AI_BUZZWORDS_HUNTING, **AI_BUZZWORDS_KERNAN}


# =========================================================
# ADDITIONAL PATTERNS FROM 6 NEW SOURCES
# =========================================================

# SOURCE 5: LitHub (via Wikipedia) – Generic positive descriptions
GENERIC_POSITIVE = {
    r"\b(revolutionary|groundbreaking|transformative|game-changing)\s+(tool|approach|method|solution)\b": 
        lambda m: f"useful {m.group(2)}",
    r"\b(incredibly|remarkably|exceptionally)\s+(important|significant|valuable)\b": r"\2",
}

# SOURCE 6: RJ Scribbles – "Not only... but also" structures
NOT_ONLY_BUT_ALSO = {
    r"\bNot only\s+([^,;.]+?),\s+but also\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(1)} and {m.group(2)}",
}

# SOURCE 7: Joshua Burdick – Negation-reframe, triple-beat, false-humble, conclusion-restate
NEGATION_REFRA ME = {
    r"\bIt's not\s+([^,;.]+?)\.\s+It's\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(2)} matters more than {m.group(1)}",
}

TRIPLE_BEAT = {
    r"\b([A-Za-z]+)\.\s+([A-Za-z]+)\.\s+([A-Za-z]+)\.\b": 
        lambda m: f"{m.group(1)}, {m.group(2)}, and {m.group(3)}",
}

FALSE_HUMBLE = {
    r"\bI used to think\s+([^,;.]+?)\.\s+Then I learned\s+([^,;.]+?)\b": 
        lambda m: f"I now understand that {m.group(2)}",
}

CONCLUSION_RESTATE = {
    r"\bIn conclusion\s+([^,;.]+?)\.\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(2)}",
}

# SOURCE 8: Quillbot – Repetitive structures, generic explanations
REPETITIVE_STRUCTURES = {
    r"\b(This|It)\s+is\s+(important|crucial|essential|vital)\s+to\s+(note|remember|understand)\b": "",
    r"\bThere\s+is\s+no\s+doubt\s+that\b": "",
    r"\bIt\s+is\s+worth\s+mentioning\s+that\b": "",
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

AI_STRUCTURAL_PATTERNS = {
    # Overly formal sentence openings
    r"\b(It is noteworthy that|It is important to note that|It should be noted that)\b": "",
    
    # Redundant introductory phrases
    r"\b(In the context of|With respect to|In terms of)\b": "Regarding",
    
    # Generic concluding statements
    r"\b(In conclusion|To summarize|Overall),\s*": "",
    
    # Passive voice triggers (convert to active where possible)
    r"\b(was|were)\s+(\w+ed)\s+by\b": r"\2",
    
    # Nominalization (turning verbs into nouns)
    r"\b(provide|offer)\s+(an?\s+)?(analysis|description|explanation)\s+of\b": r"analyze",
    r"\b(conduct|perform)\s+(an?\s+)?(assessment|evaluation)\s+of\b": r"assess",
    r"\b(make|give)\s+(an?\s+)?(argument|statement)\s+that\b": r"argue",
}

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


# =========================================================
# PHASE 2: DEEP STRUCTURAL REWRITING (BREAK AI SIGNATURE)
# =========================================================

def add_human_variation(text):
    """
    Apply deep structural transformations that force human-like unpredictability.
    Each transformation is applied with random probability (not always, not never).
    """
    
    # 1. Split into sentences
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if len(sentences) < 3:
        return text
    
    # 2. Randomly reorder some sentences (30% chance per sentence pair)
    if len(sentences) > 4 and random.random() < 0.3:
        # Swap two non-adjacent sentences
        idx1 = random.randint(0, len(sentences)-2)
        idx2 = random.randint(idx1+2, len(sentences)-1)
        sentences[idx1], sentences[idx2] = sentences[idx2], sentences[idx1]
    
    # 3. Randomly split or combine sentences
    new_sentences = []
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        words = sent.split()
        
        # Option A: Split long sentence (35% chance if >20 words)
        if len(words) > 20 and random.random() < 0.35:
            # Find a natural break point (comma, conjunction, or preposition)
            break_points = [j for j in range(10, len(words)-5) 
                          if words[j][-1] in ',;:.' or words[j].lower() in ['and', 'but', 'or', 'so', 'because']]
            if break_points:
                split_idx = random.choice(break_points)
                first = " ".join(words[:split_idx+1])
                second = " ".join(words[split_idx+1:])
                # Capitalize second
                if second:
                    second = second[0].upper() + second[1:]
                new_sentences.append(first)
                new_sentences.append(second)
                i += 1
            else:
                new_sentences.append(sent)
        # Option B: Combine with next sentence (30% chance if both <10 words)
        elif (i < len(sentences) - 1 and 
              len(words) < 10 and 
              len(sentences[i+1].split()) < 10 and
              random.random() < 0.3):
            combined = sent + " " + sentences[i+1].lower()
            new_sentences.append(combined)
            i += 2
            continue
        else:
            new_sentences.append(sent)
        i += 1
    
    # 4. Inject occasional sentence fragments (15% chance)
    if len(new_sentences) > 3 and random.random() < 0.15:
        idx = random.randint(1, len(new_sentences)-1)
        words = new_sentences[idx].split()
        if len(words) > 5:
            # Convert to fragment by removing the first 1-2 words
            fragment_words = random.randint(1, min(2, len(words)-2))
            new_sentences[idx] = "... " + " ".join(words[fragment_words:])
    
    # 5. Add occasional rhetorical questions (20% chance)
    if len(new_sentences) > 2 and random.random() < 0.2:
        idx = random.randint(0, len(new_sentences)-2)
        if not new_sentences[idx].endswith('?'):
            # Convert a declarative sentence to question
            words = new_sentences[idx].split()
            if len(words) > 3:
                # Simple transformation: add "Does/Is/Are" at beginning
                if words[0].lower() in ['the', 'this', 'that', 'these', 'those']:
                    new_sentences[idx] = "Does " + ' '.join(words[1:]) + "?"
                elif words[0].lower() in ['it', 'he', 'she', 'they', 'we']:
                    new_sentences[idx] = "Is " + ' '.join(words[1:]) + "?"
                else:
                    new_sentences[idx] = words[0] + " – does that matter?"
    
    # 6. Rebuild text
    text = " ".join(new_sentences)
    
    # 7. Add personal/anecdotal detail injection (25% chance)
    if len(text.split()) > 40 and random.random() < 0.25:
        anecdotes = [
            "Consider this: ",
            "For context, ",
            "Think of it this way – ",
            "To put it simply, ",
            "Here's the reality: ",
        ]
        # Insert at a random position (not first sentence)
        sentences = text.split('. ')
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences)-1)
            sentences[idx] = random.choice(anecdotes) + sentences[idx].lower()
        text = ". ".join(sentences)
    
    return text

def inject_human_voice(text):
    """
    Add voice switching (1st/2nd/3rd person mix) to break AI's monotone.
    """
    # Don't apply if already has mixed voice
    has_first_person = any(word in text.lower() for word in ['i ', "i'm", "i've", "we ", "we're"])
    has_second_person = any(word in text.lower() for word in ['you ', "you're", "your "])
    
    if has_first_person and has_second_person:
        return text  # Already mixed
    
    sentences = text.split('. ')
    if len(sentences) < 3:
        return text
    
    # Randomly switch some sentences to second person
    if not has_second_person and random.random() < 0.4:
        idx = random.randint(1, min(3, len(sentences)-1))
        words = sentences[idx].split()
        if len(words) > 2:
            # Prepend "You might think" or similar
            introductions = [
                "You might think that ",
                "Consider that ",
                "You could argue that ",
            ]
            sentences[idx] = random.choice(introductions) + ' '.join(words[1:]) if len(words) > 3 else random.choice(introductions) + sentences[idx].lower()
    
    # Randomly switch some sentences to first person
    if not has_first_person and random.random() < 0.35:
        idx = random.randint(1, len(sentences)-1)
        words = sentences[idx].split()
        if len(words) > 3:
            introductions = [
                "I find that ",
                "I think ",
                "In my experience, ",
                "We often see that ",
            ]
            sentences[idx] = random.choice(introductions) + ' '.join(words[1:]) if len(words) > 3 else random.choice(introductions) + sentences[idx].lower()
    
    return '. '.join(sentences)

def add_specificity(text):
    """
    Replace generic claims with concrete details (using word lists).
    """
    # Replace generic "important" with specific context
    replacements = {
        r"\bimportant\b": random.choice(["critical", "essential", "key", "notable", "worth attention"]),
        r"\bsignificant\b": random.choice(["substantial", "meaningful", "noticeable", "real"]),
        r"\bhelp\b": random.choice(["support", "assist", "aid", "make it easier"]),
        r"\buse\b": random.choice(["apply", "utilize", "employ", "work with"]),
        r"\bshow\b": random.choice(["demonstrate", "reveal", "indicate", "suggest"]),
        r"\bgood\b": random.choice(["effective", "beneficial", "solid", "reliable"]),
        r"\bbad\b": random.choice(["problematic", "harmful", "troubling", "challenging"]),
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Add concrete numbers/examples (simulated)
    if random.random() < 0.15 and len(text.split()) > 30:
        # Insert a statistic-like phrase
        stats = [
            " about 60-70% of the time",
            " in roughly 8 out of 10 cases",
            " affecting nearly three-quarters of users",
            " with around 40% reporting improvement",
        ]
        # Find a suitable place (after a verb)
        sentences = text.split('. ')
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences)-1)
            words = sentences[idx].split()
            if len(words) > 4:
                insert_pos = random.randint(2, len(words)-1)
                sentences[idx] = ' '.join(words[:insert_pos]) + random.choice(stats) + ' ' + ' '.join(words[insert_pos:])
            text = '. '.join(sentences)
    
    return text


# =========================================================
# APPLY ALL PATTERN-BASED FILTERS FROM EXTERNAL GUIDES
# =========================================================

def normalize_em_dashes(text):
    """SOURCE: Hunting the Muse – Convert unspaced em dashes to spaced"""
    for pattern, replacement in EM_DASH_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def remove_sass_phrases(text):
    """SOURCE: Hunting the Muse – Remove forced conflict creators"""
    for pattern, replacement in SASS_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def replace_ai_buzzwords(text):
    """SOURCE: Hunting the Muse + Sean Kernan – Replace overused AI vocabulary"""
    for pattern, replacement in AI_BUZZWORDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_stock_phrases(text):
    """SOURCE: Wandering Educators – Remove filler stock phrases"""
    for pattern, replacement in STOCK_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def break_parallelism(text):
    """SOURCE: Sean Kernan – Rewrite repetitive 'not X but Y' structures"""
    for pattern, replacement in PARALLELISM_PATTERNS.items():
        # Use lambda for dynamic replacement
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    return text

def neutralize_hedging(text):
    """SOURCE: Sean Kernan – Replace excessive hedging"""
    for pattern, replacement in HEDGING_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_blog_cliches(text):
    """SOURCE: Sean Kernan – Strip blogging clichés"""
    for pattern, replacement in BLOG_CLICHES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_transition_crutches(text):
    """SOURCE: Wandering Educators – Remove excessive transitions"""
    for pattern, replacement in TRANSITION_CRUTCHES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def neutralize_generic_claims(text):
    """SOURCE: AI Detector Checker – Replace vague importance claims"""
    for pattern, replacement in GENERIC_CLAIMS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def humanize_ai_patterns(text):
    """Apply all pattern-based filters from external guides in sequence"""
    text = normalize_em_dashes(text)
    text = remove_sass_phrases(text)
    text = replace_ai_buzzwords(text)
    text = remove_stock_phrases(text)
    text = break_parallelism(text)
    text = neutralize_hedging(text)
    text = remove_blog_cliches(text)
    text = remove_transition_crutches(text)
    text = neutralize_generic_claims(text)
    return text


# =========================================================
# STRUCTURAL TRANSFORMATIONS
# =========================================================

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
# DEEP HUMANIZE – APPLY ALL NEW PATTERNS FROM 6 SOURCES
# =========================================================

def deep_humanize(text):
    """
    Apply all deep rewriting passes including new patterns from 6 additional sources.
    """
    # 1. Remove generic positive hype (LitHub)
    for pattern, replacement in GENERIC_POSITIVE.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 2. Break "Not only... but also" (RJ Scribbles)
    for pattern, replacement in NOT_ONLY_BUT_ALSO.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # 3. Break negation-reframe (Joshua Burdick)
    for pattern, replacement in NEGATION_REFRA ME.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # 4. Break triple-beat (Joshua Burdick)
    for pattern, replacement in TRIPLE_BEAT.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # 5. Remove false-humble (Joshua Burdick)
    for pattern, replacement in FALSE_HUMBLE.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # 6. Remove conclusion restatement (Joshua Burdick)
    for pattern, replacement in CONCLUSION_RESTATE.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # 7. Remove repetitive structures (Quillbot)
    for pattern, replacement in REPETITIVE_STRUCTURES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 8. Apply structural variations (existing)
    text = add_human_variation(text)
    text = inject_human_voice(text)
    text = add_specificity(text)
    
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
    # Step 1: Structural fixes for AI-generated text
    text = humanize_ai_structure(text)
    
    # Step 2: Pattern-based fixes from all external guides
    text = humanize_ai_patterns(text)
    
    # Step 3: DEEP REWRITING – Break AI statistical signature
    text = deep_humanize(text)
    
    # Step 4: Expand contractions (with 30% skip)
    text = expand_contractions(text)
    
    # Step 5: Replace common words (context-aware, probability gate)
    text = replace_common_words(text)
    
    # Step 6: Add transitions (randomized)
    text = improve_transitions(text)
    
    # Step 7: Neutralize AI puffery
    text = neutralize_ai_puffery(text)
    
    # Step 8: Neutralize vague attribution
    text = neutralize_vague_attribution(text)
    
    # Step 9: Clean spacing and capitalization
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
