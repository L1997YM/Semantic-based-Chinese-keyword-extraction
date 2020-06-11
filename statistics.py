import jieba.posseg as pseg
from collections import defaultdict
import jieba.analyse as ayse
#ayse.set_idf_path("./idf.txt")

NOT_ALLOW_TAGS = ['x', 'w']
# 词性过滤文件(保留形容词、副形词、名形词、成语、简称略语、习用语、动词、动语素、副动词、名动词、名词、地名、音译地名、机构团体名、其他专名)
ALLOW_SPEECH_TAGS = ['a', 'ad', 'an', 'i', 'j', 'l', 'v', 'vg', 'vd', 'vn', 'n', 'ns', 'nsf', 'nt', 'nz']


def sentence_segmentation(text):
    wordData = []
    psegDataList = pseg.cut(text)
    for data in psegDataList:
        wordData.append(data.word)
    return wordData


def getLoc(wordsData, interDensity, title, firstSentence, lastSentence):
    wordsLoc = defaultdict(float)
    minWord = min(interDensity, key=interDensity.get)
    minValue = interDensity[minWord]
    maxWord = min(interDensity, key=interDensity.get)
    maxValue = interDensity[maxWord]
    # 提取词语的位置特征

    for word in wordsData:
        wordsLoc[word] = 0.5
        if interDensity[word] >= 0.5 * (maxValue + minValue):
            if word in title:
                wordsLoc[word] += 0.5
            elif word in firstSentence or word in lastSentence:
                wordsLoc[word] += 0.3

    return wordsLoc


def getTextRank(length, text):
    tags = ayse.textrank(text, topK=length, withWeight=True, allowPOS=ALLOW_SPEECH_TAGS)
    textRankScore = defaultdict(float)
    for item in tags:
        textRankScore[item[0]] = item[1]
    return textRankScore


def getTfidf(length, text):
    tags = ayse.extract_tags(text, topK=length, withWeight=True, allowPOS=ALLOW_SPEECH_TAGS)
    tfidf = defaultdict(float)
    for item in tags:
        tfidf[item[0]] = item[1]
    return tfidf


def getFlag(wordsFlag, wordsData):
    flagWeight = defaultdict(float)
    flagWeight['n'] = 1
    flagWeight['j'] = 0.8
    flagWeight['nr'] = 1
    flagWeight['ns'] = 1
    flagWeight['nsf'] = 0.8
    flagWeight['nt'] = 0.8
    flagWeight['nz'] = 0.8
    flagWeight['an'] = 0.5
    flagWeight['l'] = 0.5
    flagWeight['vn'] = 0.5
    flagWeight['i'] = 0.4
    flagWeight['a'] = 0.4
    flagWeight['vd'] = 0.4
    flagWeight['ad'] = 0.3
    flagWeight['v'] = 0.3
    flagWeight['vg'] = 0.3

    wordsFlagWeight = defaultdict(float)
    for word in wordsData:
        wordsFlagWeight[word] = flagWeight[wordsFlag[word]]

    return wordsFlagWeight


def getTextRank1(length, text):
    tags = ayse.textrank(text, topK=length, withWeight=True)
    textRankScore = defaultdict(float)
    for item in tags:
        textRankScore[item[0]] = item[1]
    return textRankScore


def getTfidf1(length, text):
    tags = ayse.extract_tags(text, topK=length, withWeight=True)
    tfidf = defaultdict(float)
    for item in tags:
        tfidf[item[0]] = item[1]
    return tfidf
