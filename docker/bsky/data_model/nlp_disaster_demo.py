from preprocess import preprocess_dataframe
import numpy as np
import pandas as pd
import joblib

def main():
    df = pd.read_csv('./datasets/lahaina-label.tsv',sep='\t')
    df['sentiment'].value_counts()
    # remove blanks and empty strings
    # applies preprocessing (stored in ['cleaned'])
    # extracts locations and stores in ['locations']
    df = preprocess_dataframe(df) # remove blanks and empty strings

    # Split the data to train and test sets
    from sklearn.model_selection import train_test_split
    X = df['cleaned']
    y = df['sentiment']
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=30)

    # Create pipeline
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC

    text_clf = Pipeline([('tfidf',TfidfVectorizer(sublinear_tf=True)),('clf',LinearSVC(class_weight='balanced'))])
    text_clf.fit(X_train,y_train)
    predictions = text_clf.predict(X_test)

    # Measure the model's performance
    from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
    print(confusion_matrix(y_test,predictions))
    print(classification_report(y_test,predictions))
    print(accuracy_score(y_test,predictions))

    # Export the model to be used elsewhere:
    #joblib.dump(text_clf, 'disaster_classification_model.pkl')

if __name__ == "__main__":
    main()
