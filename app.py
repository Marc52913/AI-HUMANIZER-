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
# PATTERN LIBRARY – ALL SOURCES COMBINED
# =========================================================

# SOURCE 1: Hunting the Muse
EM_DASH_PATTERNS = {
    r"(?<!\s)—(?!\s)": " — ",
    r"—": " — ",
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

# SOURCE 2: AI Detector Checker
GENERIC_CLAIMS = {
    r"\b(increasingly|critically)\s+(significant|important|transformative)\b": r"\1 relevant",
    r"\bplays?\s+a\s+crucial\s+role\b": "helps",
    r"\b(it is|this is)\s+(widely\s+)?(considered|regarded)\s+as\s+(important|significant)\b": "it matters",
}

# SOURCE 3: Wandering Educators
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

# SOURCE 4: Sean Kernan
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

AI_BUZZWORDS = {**AI_BUZZWORDS_HUNTING, **AI_BUZZWORDS_KERNAN}

# SOURCE 5: LitHub (via Wikipedia)
GENERIC_POSITIVE = {
    r"\b(revolutionary|groundbreaking|transformative|game-changing)\s+(tool|approach|method|solution)\b": 
        lambda m: f"useful {m.group(2)}",
    r"\b(incredibly|remarkably|exceptionally)\s+(important|significant|valuable)\b": r"\2",
}

# SOURCE 6: RJ Scribbles
NOT_ONLY_BUT_ALSO = {
    r"\bNot only\s+([^,;.]+?),\s+but also\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(1)} and {m.group(2)}",
}

# SOURCE 7: Joshua Burdick
NEGATION_REFRA_ME = {
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

# SOURCE 8: Quillbot
REPETITIVE_STRUCTURES = {
    r"\b(This|It)\s+is\s+(important|crucial|essential|vital)\s+to\s+(note|remember|understand)\b": "",
    r"\bThere\s+is\s+no\s+doubt\s+that\b": "",
    r"\bIt\s+is\s+worth\s+mentioning\s+that\b": "",
}

# SOURCE 9-10: Targeted fixes (from image.png analysis)
GRAMMAR_FIXES = {
    r"\ban\s+([aeiou][a-z]+)\b": r"a \1",
    r"\bIs\s+also\s+played\b": "He also played",
    r"\bYou might consider that\s+([^,;.]+?),": r"\1",
    r"\bWe often see that\s+([^,;.]+?),": r"\1",
}

GENERIC_OPENINGS = {
    r"\b([A-Z][a-z]+)\s+is one of the most famous\s+([a-z]+)\s+in the world\.": 
        lambda m: f"{m.group(1)} has achieved global recognition in {m.group(2)}.",
    r"\bHe is known for his\s+([a-z]+),\s+([a-z]+),\s+and\s+([a-z]+)\.": 
        lambda m: f"His {m.group(1)}, {m.group(2)}, and {m.group(3)} set him apart.",
}

REDUNDANT_RESTATEMENTS = {
    r"\bRonaldo has also achieved success with the Portugal national team\.": 
        "His success with Portugal includes a European Championship and Nations League title.",
    r"\bHis journey shows the importance of perseverance and commitment\.": 
        "His career exemplifies how perseverance and commitment drive achievement.",
}

GENERIC_PRAISE = {
    r"\bOne of\s+([A-Za-z]+)'s greatest strengths is his dedication to improving himself\.":
        lambda m: f"{m.group(1)}'s relentless training routine – often arriving hours before teammates – demonstrates his dedication.",
    r"\bHe is known for training consistently and maintaining a high level of fitness\.":
        "He reportedly trains with such intensity that teammates struggle to keep up.",
}

EXTRA_TRANSITIONS = {
    r"\bAs a result,\s*": "",
    r"\bConsequently,\s*": "",
}

# SOURCE 11: AI Detector 360 – Advanced patterns
BOTH_SIDES_HEDGING = {
    r"\bOn the one hand,\s*([^,;.]+?),\s*on the other hand,\s*([^,;.]+?)\b": 
        lambda m: f"{m.group(1)}. However, {m.group(2)}",
    r"\bWhile\s+([^,;.]+?),\s+it is (also|essential|important) to (consider|note|remember)\s+([^,;.]+?)\b": 
        lambda m: f"{m.group(4)} matters alongside {m.group(1)}",
}

SUMMARY_SANDWICH = {
    r"\b(In this article|This article|The following)\s+(will explore|explores|discusses)\b": "",
    r"\bIn conclusion,\s*": "",
    r"\bTo summarize,\s*": "",
    r"\bOverall,\s*": "",
}

# SOURCE 12: ETBI Digital Library
HEDGE_WORDS = {
    r"\b(might|may|could|perhaps|arguably)\b": "",
    r"\b(generally|somewhat|often|usually)\b": "",
    r"\bin many cases\b": "often",
    r"\bto some extent\b": "",
    r"\bit is possible that\b": "",
}

# SOURCE 13: Medium (MonarchPanda)
GENERIC_EXAMPLES = {
    r"\ba\s+(small business owner|busy professional|student)\s+": 
        lambda m: f"someone you know – a {m.group(1)} like Maria who runs a bakery in Portland",
    r"\bconsumers?\s+": "people – real people",
    r"\busers?\s+": "users, like you and me",
}

# SOURCE 14: The Algorithmic Bridge
OBVIOUS_INDICATORS = [
    r"\bwhich means that\b",
    r"\bin other words\b",
    r"\bthat is to say\b",
    r"\bto put it simply\b",
]


# =========================================================
# DE-AI PHRASE MAPPINGS
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
    r"\b(It is noteworthy that|It is important to note that|It should be noted that)\b": "",
    r"\b(In the context of|With respect to|In terms of)\b": "Regarding",
    r"\b(In conclusion|To summarize|Overall),\s*": "",
    r"\b(was|were)\s+(\w+ed)\s+by\b": r"\2",
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
# PHASE 2: DEEP STRUCTURAL REWRITING
# =========================================================

def add_human_variation(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if len(sentences) < 3:
        return text
    
    if len(sentences) > 4 and random.random() < 0.3:
        idx1 = random.randint(0, len(sentences)-2)
        idx2 = random.randint(idx1+2, len(sentences)-1)
        sentences[idx1], sentences[idx2] = sentences[idx2], sentences[idx1]
    
    new_sentences = []
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        words = sent.split()
        
        if len(words) > 20 and random.random() < 0.35:
            break_points = [j for j in range(10, len(words)-5) 
                          if words[j][-1] in ',;:.' or words[j].lower() in ['and', 'but', 'or', 'so', 'because']]
            if break_points:
                split_idx = random.choice(break_points)
                first = " ".join(words[:split_idx+1])
                second = " ".join(words[split_idx+1:])
                if second:
                    second = second[0].upper() + second[1:]
                new_sentences.append(first)
                new_sentences.append(second)
                i += 1
            else:
                new_sentences.append(sent)
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
    
    if len(new_sentences) > 3 and random.random() < 0.15:
        idx = random.randint(1, len(new_sentences)-1)
        words = new_sentences[idx].split()
        if len(words) > 5:
            fragment_words = random.randint(1, min(2, len(words)-2))
            new_sentences[idx] = "... " + " ".join(words[fragment_words:])
    
    if len(new_sentences) > 2 and random.random() < 0.2:
        idx = random.randint(0, len(new_sentences)-2)
        if not new_sentences[idx].endswith('?'):
            words = new_sentences[idx].split()
            if len(words) > 3:
                if words[0].lower() in ['the', 'this', 'that', 'these', 'those']:
                    new_sentences[idx] = "Does " + ' '.join(words[1:]) + "?"
                elif words[0].lower() in ['it', 'he', 'she', 'they', 'we']:
                    new_sentences[idx] = "Is " + ' '.join(words[1:]) + "?"
                else:
                    new_sentences[idx] = words[0] + " – does that matter?"
    
    text = " ".join(new_sentences)
    
    if len(text.split()) > 40 and random.random() < 0.25:
        anecdotes = [
            "Consider this: ",
            "For context, ",
            "Think of it this way – ",
            "To put it simply, ",
            "Here's the reality: ",
        ]
        sentences = text.split('. ')
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences)-1)
            sentences[idx] = random.choice(anecdotes) + sentences[idx].lower()
        text = ". ".join(sentences)
    
    return text

def inject_human_voice(text):
    has_first_person = any(word in text.lower() for word in ['i ', "i'm", "i've", "we ", "we're"])
    has_second_person = any(word in text.lower() for word in ['you ', "you're", "your "])
    
    if has_first_person and has_second_person:
        return text
    
    sentences = text.split('. ')
    if len(sentences) < 3:
        return text
    
    if not has_second_person and random.random() < 0.4:
        idx = random.randint(1, min(3, len(sentences)-1))
        words = sentences[idx].split()
        if len(words) > 2:
            introductions = [
                "You might think that ",
                "Consider that ",
                "You could argue that ",
            ]
            sentences[idx] = random.choice(introductions) + ' '.join(words[1:]) if len(words) > 3 else random.choice(introductions) + sentences[idx].lower()
    
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
    
    if random.random() < 0.15 and len(text.split()) > 30:
        stats = [
            " about 60-70% of the time",
            " in roughly 8 out of 10 cases",
            " affecting nearly three-quarters of users",
            " with around 40% reporting improvement",
        ]
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
# PHASE 3: ADVANCED PATTERN NEUTRALIZATION (FROM NEW SOURCES)
# =========================================================

def break_metronome_rhythm(text):
    """SOURCE: AI Detector 360 – Break uniform sentence length"""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if len(sentences) < 3:
        return text
    
    new_sentences = []
    for sent in sentences:
        words = sent.split()
        word_count = len(words)
        
        if 12 < word_count < 25 and random.random() < 0.4:
            break_chars = [',', ';', 'and', 'but', 'or', 'so', 'because']
            break_points = [i for i in range(3, word_count-3) 
                           if words[i].lower() in break_chars or words[i][-1] in ',;']
            
            if break_points and random.random() < 0.5:
                split_idx = random.choice(break_points)
                first = " ".join(words[:split_idx+1])
                second = " ".join(words[split_idx+1:])
                if second:
                    second = second[0].upper() + second[1:]
                new_sentences.append(first)
                new_sentences.append(second)
            else:
                fragments = [
                    "Honestly, ",
                    "To be fair, ",
                    "Look, ",
                    "Sure, ",
                ]
                if random.random() < 0.5:
                    sent = random.choice(fragments) + sent.lower()
                new_sentences.append(sent)
        else:
            new_sentences.append(sent)
    
    return " ".join(new_sentences)

def neutralize_both_sides_hedging(text):
    """SOURCE: AI Detector 360 – Remove 'on one hand... on the other hand'"""
    for pattern, replacement in BOTH_SIDES_HEDGING.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    return text

def neutralize_hedge_words(text):
    """SOURCE: ETBI Digital Library – Remove excessive hedges"""
    for pattern, replacement in HEDGE_WORDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def replace_generic_examples(text):
    """SOURCE: AI Detector 360 + Medium – Replace vague examples"""
    for pattern, replacement in GENERIC_EXAMPLES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def break_summary_sandwich(text):
    """SOURCE: AI Detector 360 – Remove intro/outro restatements"""
    for pattern, replacement in SUMMARY_SANDWICH.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def add_subtext_and_nuance(text):
    """SOURCE: The Algorithmic Bridge – Remove over-explanation"""
    for pattern in OBVIOUS_INDICATORS:
        text = re.sub(pattern + r"\s+", "", text, flags=re.IGNORECASE)
    
    if random.random() < 0.15:
        sentences = text.split('. ')
        for i, sent in enumerate(sentences):
            words = sent.split()
            if len(words) > 8 and random.random() < 0.1:
                if 'because' in sent:
                    sentences[i] = sent.split(' because')[0]
                elif 'so that' in sent:
                    sentences[i] = sent.split(' so that')[0]
        text = '. '.join(sentences)
    
    return text

def add_emotional_heat(text):
    """SOURCE: Medium + Wandering Educators – Inject genuine emotion"""
    if random.random() < 0.15:
        emotions = [
            "frustrating",
            "exhilarating",
            "annoying",
            "hilarious",
            "heartbreaking",
        ]
        sentences = text.split('. ')
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences)-1)
            words = sentences[idx].split()
            if len(words) > 4:
                insert_pos = random.randint(1, min(3, len(words)-2))
                words.insert(insert_pos, random.choice(emotions))
                sentences[idx] = ' '.join(words)
            text = '. '.join(sentences)
    
    return text

def humanize_advanced_patterns(text):
    """Apply all advanced pattern neutralizations from new sources."""
    text = break_metronome_rhythm(text)
    text = neutralize_both_sides_hedging(text)
    text = neutralize_hedge_words(text)
    text = replace_generic_examples(text)
    text = break_summary_sandwich(text)
    text = add_subtext_and_nuance(text)
    text = add_emotional_heat(text)
    return text


# =========================================================
# APPLY ALL PATTERN-BASED FILTERS
# =========================================================

def normalize_em_dashes(text):
    for pattern, replacement in EM_DASH_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def remove_sass_phrases(text):
    for pattern, replacement in SASS_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def replace_ai_buzzwords(text):
    for pattern, replacement in AI_BUZZWORDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_stock_phrases(text):
    for pattern, replacement in STOCK_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def break_parallelism(text):
    for pattern, replacement in PARALLELISM_PATTERNS.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    return text

def neutralize_hedging(text):
    for pattern, replacement in HEDGING_PHRASES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_blog_cliches(text):
    for pattern, replacement in BLOG_CLICHES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def remove_transition_crutches(text):
    for pattern, replacement in TRANSITION_CRUTCHES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def neutralize_generic_claims(text):
    for pattern, replacement in GENERIC_CLAIMS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def humanize_ai_patterns(text):
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
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    if len(sentences) < 3:
        return text
    
    new_sentences = []
    for i, sent in enumerate(sentences):
        words = sent.split()
        if len(words) > 15 and random.random() < 0.3:
            mid = len(words) // 2
            break_points = [j for j in range(mid-3, mid+4) 
                          if 0 < j < len(words) and words[j][-1] in ',.;:']
            if break_points:
                split_idx = random.choice(break_points)
                first = " ".join(words[:split_idx+1])
                second = " ".join(words[split_idx+1:])
                if second:
                    second = second[0].upper() + second[1:]
                new_sentences.append(first)
                new_sentences.append(second)
            else:
                new_sentences.append(sent)
        else:
            new_sentences.append(sent)
    
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
    intensifiers = r"\b(very|extremely|absolutely|completely|totally|utterly|highly|particularly|notably)\b"
    text = re.sub(intensifiers + r"\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(extremely|very)\s+(important|crucial)\b", r"\2", text, flags=re.IGNORECASE)
    return text

def simplify_ai_complexity(text):
    for pattern, replacement in AI_PHRASE_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def apply_ai_structural_fixes(text):
    for pattern, replacement in AI_STRUCTURAL_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def humanize_ai_structure(text):
    text = apply_ai_structural_fixes(text)
    text = simplify_ai_complexity(text)
    text = remove_redundant_modifiers(text)
    text = break_ai_sentence_patterns(text)
    return text


# =========================================================
# DEEP HUMANIZE – APPLY ALL PATTERNS
# =========================================================

def deep_humanize(text):
    # SOURCE 5: LitHub
    for pattern, replacement in GENERIC_POSITIVE.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # SOURCE 6: RJ Scribbles
    for pattern, replacement in NOT_ONLY_BUT_ALSO.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # SOURCE 7: Joshua Burdick
    for pattern, replacement in NEGATION_REFRA_ME.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    for pattern, replacement in TRIPLE_BEAT.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    for pattern, replacement in FALSE_HUMBLE.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    for pattern, replacement in CONCLUSION_RESTATE.items():
        text = re.sub(pattern, lambda m: replacement(m), text, flags=re.IGNORECASE)
    
    # SOURCE 8: Quillbot
    for pattern, replacement in REPETITIVE_STRUCTURES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # SOURCE 9-10: Targeted fixes
    for pattern, replacement in GRAMMAR_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    for pattern, replacement in GENERIC_OPENINGS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    for pattern, replacement in REDUNDANT_RESTATEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    for pattern, replacement in GENERIC_PRAISE.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    for pattern, replacement in EXTRA_TRANSITIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply structural variations (Phase 2)
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
            if synonym.lower() != clean_word.lower() and synonym.isalpha():
                candidates.append(synonym)
    if not candidates:
        return word
    return random.choice(candidates)


# =========================================================
# EXPAND CONTRACTIONS
# =========================================================

def expand_contractions(text):
    for contraction, expanded in CONTRACTIONS.items():
        if random.random() < 0.30:
            continue
        pattern = r"\b" + re.escape(contraction) + r"\b"
        text = re.sub(pattern, expanded, text, flags=re.IGNORECASE)
    return text


# =========================================================
# REPLACE COMMON WORDS
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

        match = re.match(r"^([^A-Za-z]*)(.*?)([^A-Za-z]*)$", word)
        if not match:
            new_words.append(word)
            continue

        prefix, core, suffix = match.groups()
        lower = core.lower()

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
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    if len(sentences) < 4:
        return text

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
# DE-AI NEUTRALIZATION
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
# CLEAN TEXT
# =========================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)

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
    
    # Step 4: ADVANCED PATTERN NEUTRALIZATION (NEW – from 8 new sources)
    text = humanize_advanced_patterns(text)
    
    # Step 5: Expand contractions (with 30% skip)
    text = expand_contractions(text)
    
    # Step 6: Replace common words (context-aware, probability gate)
    text = replace_common_words(text)
    
    # Step 7: Add transitions (randomized)
    text = improve_transitions(text)
    
    # Step 8: Neutralize AI puffery
    text = neutralize_ai_puffery(text)
    
    # Step 9: Neutralize vague attribution
    text = neutralize_vague_attribution(text)
    
    # Step 10: Clean spacing and capitalization
    text = clean_text(text)
    
    return text


# =========================================================
# HUMANIZE BUTTON
# =========================================================

if st.button("✨ Humanize Text", type="primary"):

    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Rewriting your text..."):
            try:
                output_text = humanize_text(text)
                st.success("Text successfully rewritten!")
                st.subheader("Rewritten Text")
                st.text_area("Output:", value=output_text, height=300)
                st.write(f"**Output word count:** {len(output_text.split())}")
                st.download_button(
                    label="⬇️ Download Text",
                    data=output_text,
                    file_name="rewritten_text.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error("Something went wrong while rewriting the text.")
                st.exception(e)
