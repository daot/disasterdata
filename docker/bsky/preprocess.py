from nlp_loader import get_nlp, get_p
import emoji
import re

# get a list of tokens to process
def spacy_tokenize(text, nlp):
    return [t.text for t in nlp(text)]

# removes all non alpha-numeric characters
def strip_punct(text):
    text = re.sub('[^A-Za-z0-9 ]+','', text)
    return text

'''
Does the following:
- converts emojis to their descriptions without punctuation
- strips hashtags of their # symbols
- removes user mentions entirely
- removes urls entirely
- converts numbers to words for consistency

Be aware that an empty string may be returned.
To save on loading time, the process using this module should use the nlp_loader to pre-load
spacy and the inflect engine with nlp_loader modules, then pass them in as arguments.
'''
def bsk_preprocessor(text, nlp=get_nlp(), p=get_p()):
    text = text.encode("utf-8").decode("unicode_escape")
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove urls
    text = re.sub(r"\@\w+|\#", "", text)  # remove user mentions and strip hashtags

    tokens = spacy_tokenize(text, nlp)
    stop = set(nlp.Defaults.stop_words)

    final_tokens = []
    for t in tokens:
        if t.isspace() or len(t)==0: # don't add empty strings
            continue
        # convert emojis to their descriptions
        if t in emoji.EMOJI_DATA:
            final_tokens.append(re.sub('_', ' ', emoji.demojize(t).strip(':')))
        # convert numbers to text
        elif t.isnumeric():
            final_tokens.append(p.number_to_words(t))
        # skip stopwords and empty strings, include anything else
        elif t and t not in stop:
        #elif t:
            temp = strip_punct(t)
            if temp:
                final_tokens.append(strip_punct(t))
    return " ".join(final_tokens)

def bsk_preprocessor_sw(text, nlp=get_nlp(), p=get_p()):
    text = text.encode("utf-8").decode("unicode_escape")
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove urls
    text = re.sub(r"\@\w+|\#", "", text)  # remove user mentions and strip hashtags

    tokens = spacy_tokenize(text, nlp)
    stop = set(nlp.Defaults.stop_words)

    final_tokens = []
    for t in tokens:
        if t.isspace() or len(t)==0: # don't add empty strings
            continue
        # convert emojis to their descriptions
        if t in emoji.EMOJI_DATA:
            final_tokens.append(re.sub('_', ' ', emoji.demojize(t).strip(':')))
        # convert numbers to text
        elif t.isnumeric():
            final_tokens.append(p.number_to_words(t))
        # skip stopwords and empty strings, include anything else
        elif t:
            temp = strip_punct(t)
            if temp:
                final_tokens.append(strip_punct(t))
    return " ".join(final_tokens)

# Remove empty spots in the data and empty strings
def clean_dataframe(df):
    df.dropna(inplace=True)
    blanks = []
    for i,lb,post in df.itertuples():
        if post.isspace():
            blanks.append(i)
    df.drop(blanks,inplace=True)
    return df

# Get the named entities that are locations from a document
def locations(text, nlp=get_nlp()):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            loc = ent.text
            if not re.search(r"[^a-zA-Z\s.,]", loc):
                return loc
    return None

def preprocess_dataframe(df):
    nlp=get_nlp()
    p = get_p()
    df = clean_dataframe(df) # remove blanks and empty strings
    df['cleaned'] = df['text'].apply(lambda x: bsk_preprocessor(x, nlp=nlp, p=p)) # Use this one to train the data
    df.dropna()
    # df = clean_dataframe(df) # remove blanks and empty strings again
    return df

def preprocess_dataframe_sw(df):
    nlp=get_nlp()
    p = get_p()
    df = clean_dataframe(df)
    df['cleaned'] = df['text'].apply(lambda x: bsk_preprocessor_sw(x, nlp=nlp, p=p))
    df.dropna()
    return df