# Import libraries
import numpy as np
import pandas as pd
df = pd.read_csv('../TextFiles/moviereviews.tsv', sep='\t')


# Check for missing pieces of data
df.isnull().sum()


# Missing some review, remove the data points:
df.dropna(inplace=True)
df.isnull().sum()


# Some might have empty strings, remove the empty strings / whitespace reviews
blanks = []
for i,lb,rv in df.itertuples():
    if rv.isspace():
        blanks.append(i)
df.drop(blanks,inplace=True)


from sklearn.model_selection import train_test_split
X = df['review']
y = df['label']


# Split into test and training data
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=42)


# Build a pipeline to vectorize the data, then train and fit the model
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

text_clf = Pipeline([('tfidf', TfidfVectorizer()),
                     ('clf',LinearSVC())])

text_clf.fit(X_train, y_train)
predictions = text_clf.predict(X_test)


from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
print(confusion_matrix(y_test, predictions))
print(classification_report(y_test, predictions))
print(accuracy_score(y_test, predictions))





