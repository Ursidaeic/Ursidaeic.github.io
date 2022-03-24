from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

import pickle, json
from utils.PRSR import prsr
import pandas as pd


if __name__ == "__main__":
    
    with open ("resources/training_set.json", "r", encoding="utf8") as f:
        train_data = json.load(f)

    pos_processed = prsr(train_data['pos'])
    neg_processed = prsr(train_data['neg'])
    neu_processed = prsr(train_data['neu'])

    emo = pos_processed + neg_processed
    d = []
    for e in emo:
        d.append((e, "true"))
    for n in neu_processed:
        d.append((n, "false"))
    df = pd.DataFrame(data=d, columns=["comment", "t/f"])

    
    tfidf = TfidfVectorizer()
    X = df["comment"]
    y = df["t/f"]

    X = tfidf.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 1)


    clf = LinearSVC()
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print(classification_report(y_test, y_pred))
    

    with open('SVM.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(clf, f, pickle.HIGHEST_PROTOCOL)
