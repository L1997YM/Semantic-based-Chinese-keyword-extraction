import jieba.posseg as pseg
import jieba
#jieba.set_dictionary("./dict.txt")
#jieba.initialize()

import re
from collections import defaultdict
 
# 词性过滤文件(保留形容词、副形词、名形词、成语、简称略语、习用语、动词、动语素、副动词、名动词、名词、地名、音译地名、机构团体名、其他专名)
ALLOW_SPEECH_TAGS = ['a', 'ad', 'an', 'i', 'j', 'l', 'v', 'vg', 'vd', 'vn', 'n', 'ns', 'nsf', 'nt', 'nz']
NOT_ALLOW_TAGS = ['x', 'w']

# 分句
def split_sentences(text):
    pattern = r'。|！|？|;'
    sentences = re.split(pattern, text)
    return sentences

# 处理前后继词典
def addDict(preDict, afterDict, lastWord, word):
    if lastWord in afterDict:
        if word in afterDict[lastWord]:
            value = afterDict[lastWord][word] + 1
            afterDict[lastWord].update({word: value})
        else:
            afterDict[lastWord].update({word: 1})
    else:
        afterDict.update({lastWord: {word: 1}})

    if word in preDict:
        if lastWord in preDict[word]:
            value = preDict[word][lastWord] + 1
            preDict[word].update({lastWord: value})
        else:
            preDict[word].update({word: 1})
    else:
        preDict.update({word: {lastWord: 1}})


def sentence_segmentation(title):
    print('------对标题进行预处理------')
    wordData = []
    psegDataList = pseg.cut(title)
    for data in psegDataList:
        wordData.append(data.word)
    return wordData


# 预处理
def word_segmentation(body, title):
    print('------当前进行分词&词性标注&去重停用词&保留指定词性词语操作------')
    # 加载停用词文件
    stopWords = [line.strip()for line in open('dict_file/stop_words.txt', encoding='utf-8').readlines()]

    # 分句
    sentences_list = split_sentences(body)
    # 文章首句和尾句
    firstSentence = sentences_list[0]
    lastSentence = sentences_list[-1]
    sentences_list.append(title)

    # 候选关键词
    wordsData = []
    # 存储词语词性
    wordsFlagDict = defaultdict(str)
    # 储存词语的后继关系
    nextDict = {}
    # 储存词语的前继关系
    preDict = {}
    # 存储每个词语有多少个后接词语
    nextWordSum = defaultdict(int)
    # 储存每个单词有多少个前继词语
    preWordSum = defaultdict(int)


    for sentence in sentences_list:
        # jieba分词&词性标注
        psegDataList = pseg.cut(sentence)

        # 记录上一个词语的词性
        lastFlag = 'w'
        # 记录上一个词语
        lastWord = ''

        for data in psegDataList:

            # 记录词语的前继后继关系，为了处理jieba会将部分词语进一步分割的问题（如5G、云平台），实际效果一般
            if lastFlag not in NOT_ALLOW_TAGS and data.flag not in NOT_ALLOW_TAGS and data.word not in stopWords and lastWord not in stopWords:
                addDict(preDict, nextDict, lastWord, data.word)
                value = nextWordSum[lastWord] + 1
                nextWordSum.update({lastWord: value})
                value = preWordSum[data.word] + 1
                preWordSum.update({data.word: value})
            lastFlag = data.flag
            lastWord = data.word

            # 词性过滤并记录词性
            if len(data.word) > 1 and data.flag in ALLOW_SPEECH_TAGS and data.word not in stopWords:
                wordsData.append(data.word)
                wordsFlagDict[data.word] = data.flag

    # 对词语集合进行去重
    wordsData = list(set(wordsData))

    return wordsData, wordsFlagDict, firstSentence, lastSentence, nextDict, nextWordSum, preDict, preWordSum

def getkeyphrase(keywords,text):
    # 分句
    sentences_list = split_sentences(text)
    # 关键词集合
    words = []
    # 关键短语集合
    keyphrase = {}
    # 上一个关键词
    lastword = ""
    lastvalue = 0
    # 判断上一个词语是否是关键词
    flag = 0
    # 将关键词与权值建立字典
    wordDict = defaultdict(int)
    for sentence in sentences_list:
        # jieba分词&词性标注
        psegDataList = pseg.cut(sentence)
        # 将keywords中的词语读入words中
        for wordData in keywords:
            words.append(wordData[0])
            wordDict[wordData[0]] = wordData[1]
        # 判断是否存在关键短语
        for wordData in psegDataList:
            if wordData.word in words and flag == 1:
                str = lastword + wordData.word
                value = lastvalue + wordDict[wordData.word]
                keyphrase[str] = value
            if wordData.word in words and flag == 0:
                lastword = wordData.word
                lastvalue = wordDict[wordData.word]
                flag = 1
            if wordData.word not in words:
                flag = 0
    # 排序
    keyphrase_order = sorted(keyphrase.items(), key=lambda x: x[1], reverse=True)
    return keyphrase_order
