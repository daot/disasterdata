
# Start off importing libraries and our .tsv file
import numpy as np
import pandas as pd

df = pd.read_csv('../TextFiles/smsspamcollection.tsv',sep='\t')
df.head() # Confirm we've read in
df.isnull().sum() # Check for missing values
df['label'].value_counts() # Check what our categories are and how many in each


# Split the data into our training data and test data
from sklearn.model_selection import train_test_split
X = df['message']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.33,random_state=42)


# Extracting features using the CountVectorizer for example
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()


# 2 steps to use the feature extraction
# 1. FIT -- Fit the vectorizer to the data (builds a vocabulary, count number of words, ...)
# 2. TRANSFORM -- Transform the original text message --> vector
# We can do it separately or with one step:
X_train_counts = count_vect.fit_transform(X_train)


# X_train_counts is a huge sparse matrix
X_train_counts.shape


# Now using another FIT-TRANSFORM called TFIDF (term frequency inverse document frequency)
# Gives less weight to very common words like 'the' 'is', etc
from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()


X_Train_tfidf = tfidf_transformer.fit_transform(X_train_counts)


# Can also just combine CountVectorization and TfidfTransformation with: TfidfVectorizer
# This is doing the same 2 things as above, less steps:
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vect = TfidfVectorizer()
X_Train_tfidf = tfidf_vect.fit_transform(X_train)


# Now let's train a classifier
from sklearn.svm import LinearSVC
clf = LinearSVC()


# Fit it to our vectorized training data
clf.fit(X_Train_tfidf, y_train)


# It's a lot of steps to do fit-transform-classify so we can use a SciKitLearn Pipeline
from sklearn.pipeline import Pipeline
text_clf = Pipeline([('tfidf', TfidfVectorizer()),('clf',LinearSVC())]) # Pipeline objects takes a list of tuples ('Label', operation)


# Now we can do all of this in one step and immediately fit the data:
text_clf.fit(X_train, y_train)


# Now test the model again with predictions
predictions = text_clf.predict(X_test)


from sklearn.metrics import confusion_matrix,classification_report
print(confusion_matrix(y_test, predictions))

print(classification_report(y_test,predictions))





