
from tgbot.ml.nss_utils import test_nss, find_most_similar_sentence

from tgbot.backoffice.models import AiQAActivityLog, NaiveSentenceSimilarityDb


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

clf = Pipeline(
    [
        ('tfidf', TfidfVectorizer()),
        ('sgd', SGDClassifier())
    ]
)


def train_intent_classification():
    queryset = NaiveSentenceSimilarityDb.objects.all()

    X = []
    y = []

    for item in queryset:
        X.append(item.reference_sentence)
        y.append(item.action.action)

    ## Train the classifier

    clf.fit(X, y)


if __name__ == '__main__':

    train_intent_classification()

    # predicted_intents = clf.predict(["come faccio ad iscrivermi?"])
    #
    # print(predicted_intents)
    #
    #
    # exit(0)

    queryset = AiQAActivityLog.objects.order_by("-id")

    udict = {}

    results_dict = {}

    for item in queryset:

        if item.user_question in udict:
            pass

        udict[item.user_question] = item

    print(udict)
    print(len(udict))

    counter = 0

    for k,v in udict.items():

        row = [v, find_most_similar_sentence(k), None]

        predicted_intents = clf.predict([k])

        row[2] = predicted_intents[0] if len(predicted_intents) > 0 else None

        results_dict[k] = row

        counter += 1

        # if counter > 2:
        #     break

    print(results_dict)
    print()

    for k,v in results_dict.items():
        print("KEY: " + k)
        print(v[0])
        print(v[1])
        print(v[2])
        print()

    # test_nss()

    # find_most_similar_sentence("blah. ciao")

    pass

# eval http://www.nltk.org/howto/relextract.html