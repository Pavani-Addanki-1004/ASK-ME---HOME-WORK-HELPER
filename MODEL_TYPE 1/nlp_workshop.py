import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def clean_sent(sentence):
    """Cleans and tokenizes the input sentence"""
    sentence = sentence.lower()
    sentence = re.sub(r'http\S+', '', sentence)
    sentence = re.sub(r'www\S+', '', sentence)
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(sentence)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(tokens)