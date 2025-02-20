import nltk

# Download nltk stuff
nltk.download('punkt')
nltk.download('stopwords')
sw = nltk.corpus.stopwords.words('english')

# Remove empty spots in the data and empty strings
def clean_dataframe(df):
    df.dropna(inplace=True)
    blanks = []
    for i,lb,msg in df.itertuples():
        if msg.isspace():
            blanks.append(i)
    df.drop(blanks,inplace=True)
    return df

# Remove stopwords / punctuation but keep hashtags
def clean_text(text):
    # Set to lowercase and tokenize
    text = text.lower()
    words = nltk.tokenize.word_tokenize(text, language="english")
    text = " ".join([w for w in words if (w.isalpha() or w.startswith("#")) and w not in sw])
    return text

def preprocess(df):
    df = clean_dataframe(df) # remove blanks and empty strings
    df['cleaned'] = df['text'].apply(clean_text) # Use this one to train the data
    return df