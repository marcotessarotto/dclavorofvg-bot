# https://stackoverflow.com/questions/56836865/how-to-use-nlp-in-python-to-analyze-questions-from-a-chat-conversation

# Training data

## X is the sample sentences
X = [
    'Where can I find wood?',
    'What is the location of wood?',
    'Where do I find fire?',
    'Give me the coordinates of lemons.',
    'What is the best place to gather coal?',
    'Do you know where I can find tomatoes?',
    'Tell me a spot to collect wood.',
    'How can I level up strength?',
    'How do I train woodcutting?',
    'Where can I practice my swimming skill?',
    'Can I become better in running?',
    'Where can I train my woodcutting skill?'
]

## y is the intent class corresponding to sentences in X
y = [
    'find_resource',
    'find_resource',
    'find_resource',
    'find_resource',
    'find_resource',
    'find_resource',
    'find_resource',
    'improve_skill',
    'improve_skill',
    'improve_skill',
    'improve_skill',
    'improve_skill'
]

# Define the classifier

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

clf = Pipeline(
    [
        ('tfidf', TfidfVectorizer()),
        ('sgd', SGDClassifier())
    ]
)

## Train the classifier

clf.fit(X, y)

# Test your classifier

## New sentences (that weren't in X and your model never seen before)

new_sentences = [
    'What are the coordinates of wood?',
    'Where can I find paper?',
    'How can I improve woodcutting?',
    'Where can I improve my jumping skill?'
]

predicted_intents = clf.predict(new_sentences)

print(predicted_intents)

