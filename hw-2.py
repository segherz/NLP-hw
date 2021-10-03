import re
from collections import OrderedDict
from natasha import (Segmenter,
                     NewsMorphTagger, NewsEmbedding,
                     Doc)
import spacy
from sklearn.metrics import accuracy_score
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

nlp = spacy.load("ru_core_news_sm")

pos_FROM_P = {'NPRO': 'PRON', 'ADVB': 'ADV', 'PRED': 'ADV', 'VERB': 'VERB', 'PNCT': 'PUNCT', 'NOUN': 'NOUN',
              'PREP': 'ADP', 'INFN': 'VERB', 'GRND': 'VERB', 'PRCL': 'PART', 'ADJF': 'ADJ', 'ADJS': 'ADJ',
              'COMP': 'ADJ', 'CONJ': 'CCONJ', 'UNKN': 'X', 'NUMR': 'NUM', 'PRTF': 'VERB'}


def acc(dictio, name):
    a = []
    b = []
    for i in gold.keys():
        a.append(gold[i])
        b.append(dictio[i])

    print('Accuracy для ' + name + ': ' + str(accuracy_score(b, a)) + '%')
    return 0


segmenter = Segmenter()
morph_tagger = NewsMorphTagger(NewsEmbedding())

gold = OrderedDict()
slovne = OrderedDict()

with open('корпус.txt', 'r', encoding='utf-8') as f:
    text = f.read()

with open('gold.txt', 'r', encoding='utf-8') as f:
    for line in f:
        x = re.split('___', re.sub('\n', '', line))
        gold[x[0]] = x[1]

doc = Doc(text)
doc.segment(segmenter)
doc.tag_morph(morph_tagger)

for i in doc.tokens:
    x = re.search("text='.+?'", str(i)).group(0)
    x = re.sub("text='", '', x)
    x = re.sub("'", '', x)
    x = x.lower()
    y = re.search("pos='.+?'", str(i)).group(0)
    y = re.sub("pos='", '', y)
    y = re.sub("'", '', y)
    slovne[x] = y

acc(slovne, 'Slovnet')

doc = nlp(text)

spac = OrderedDict()
for i, s in enumerate(doc.sents):  # делит по дефису, фиксим как-то
    for t in s:
        if t.pos_ != 'SPACE' and t.text != 'какой':
            spac[t.text.lower()] = t.pos_
        else:
            spac['какой-то'] = 'DET'

acc(spac, 'spaCy')

with open('леммы.txt', 'r', encoding='utf-8') as f:
    lemma = f.read()
    lemmas = lemma.split('\n')

pymorph = OrderedDict()
for l in lemmas:
    p = morph.parse(l)[0]
    if str(p.tag) != 'PNCT':
        pymorph[l] = pos_FROM_P[str(p.tag.POS)]
    else:
        pymorph[l] = pos_FROM_P[str(p.tag)]

a = []
b = []
for i in gold.keys():
    a.append(gold[i])
    b.append(pymorph[i])

acc(pymorph, 'pymorphy2')
