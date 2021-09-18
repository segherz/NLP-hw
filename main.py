import urllib.request
import re
import time
import nltk
import pymorphy2
from sklearn.metrics import accuracy_score
from collections import Counter

morph = pymorphy2.MorphAnalyzer()

url = f'https://otzovik.com/reviews/smartphone_xiaomi_redmi_7/<page_number>/?ratio=<score>'  # итерировать по page_number и score (оценка пользователя)
uurl = f'https://otzovik.com/reviews/smartphone_xiaomi_redmi_7/?ratio=5'


def tokenized_text(text):
    text = text.lower()
    text = re.sub('\W', ' ', text)
    g = nltk.word_tokenize(text)
    return g


def file_deal(path, list):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        for tok in tokenized_text(text):
            if tok.isalpha():
                list.append(morph.parse(tok)[0].normal_form)
    return list


def freq_count(list):
    cnt = Counter(list)
    d = []
    for w in cnt.elements():
        if cnt[w] < 3:
            d.append(w)
    for w in d:
        del cnt[w]
    return cnt


good_rev = []
file_deal(r'good.txt', good_rev)

bad_rev = []
file_deal(r'bad.txt', bad_rev)

# only_good = set(good_rev).difference(set(bad_rev))
# only_bad = set(bad_rev).difference(set(good_rev))

b_cnt = freq_count(bad_rev)  #это чтобы убрать нечастотные
g_cnt = freq_count(good_rev)

only_good = set(g_cnt.elements()).difference(set(b_cnt.elements()))
only_bad = set(b_cnt.elements()).difference(set(g_cnt.elements()))


def get_links(url):
    page = urllib.request.urlopen(url)
    text = page.read().decode('utf-8')
    reviews = re.findall('<a class="review-btn review-read-link" href="(.+?)">', text)
    return reviews


def parce(url):
    page = urllib.request.urlopen(url)
    text = page.read().decode('utf-8')
    review = re.findall(r'</div><br>(.+?)</div>', text)
    clear_review = re.sub('<.+?>', '', review[0])
    return clear_review


def rev(url, page, score):  # функция не работает из-за того, что сайт стал недоступен. Но он был!! Прошлые две функции раньше (когда-то) работали!
    url = re.sub('<page_number>', page, url)
    url = re.sub('<score>', score, url)
    list_of_links = get_links(url)  # сайт перестал пускать как раз после работы этой функции, потом снова заработал,
    reviews = [] # но костыль в виде time.sleep() не помог, а больше я не умею пока...
    # reviews = ''
    for link in list_of_links:
        reviews.append(parce('https://otzovik.com' + link))
        time.sleep(5)
        # альтернативный вариант, но его запустить я уже не смогла из-за недоступности сайта:
        # reviews += str(parce('https://otzovik.com' + link))
        # time.sleep(5)
        # и далее токенизировать строку с помощью верхних функций
    return reviews


def check_review(review, good, bad):
    g = 0
    b = 0
    for token in tokenized_text(review):
        if token in good:
            g += 1  # тут можно взвешенное -- += g_cnt[token] (кол-во вхождений)
        elif token in bad:
            b += 1  # и тут
    if b > g:
        return 'negative'
    else:
        return 'positive'


def get_control_reviews(path, spl='123456'):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        text = text.lower()
        l = text.split(spl)
        lines = []
        for line in l:
            line = re.sub('\W', ' ', line)
            tokens = tokenized_text(line)
            new = ''
            for t in tokens:
                tt = morph.parse(t)[0].normal_form
                new += tt
                new += ' '
            lines.append(new)
    return lines


def accuracy_test(control_corpus):
    results = []
    reality = []
    for r in control_corpus.keys():
        results.append(check_review(r, only_good, only_bad))
        reality.append(control_corpus[r])
    return accuracy_score(results, reality)


control = {}

neg = get_control_reviews(r'check_bad.txt')
pos = get_control_reviews(r'check_good.txt')

for x in neg:
    control[x] = 'negative'
for x in pos:
    control[x] = 'positive'

print(accuracy_test(control))