from nltk.corpus import stopwords
from nltk import word_tokenize

stoplist = set(stopwords.words('english'))

sent = "The quick brown fox jumps over the lazy dog"

tokenized_sent = word_tokenize(sent.lower())
tokenized_sent_nostop = [token for token in tokenized_sent if token not in stoplist]

print(tokenized_sent_nostop)

