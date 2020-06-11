import dijkstra
from collections import defaultdict
import similarity


# 计算指定顶点的居间度
# 传入参数：指定顶点，最短路径信息
def intermediaryDegreeScore(word, shortestDatas):
    Score = 0
    for m in shortestDatas.keys():
        for k in shortestDatas.keys():
            if m == k:
                continue
            else:
                # 计算词语居间度
                try:
                    path = shortestDatas[m][k]['path']
                    if word in path:
                        Score += 1
                except:
                    continue
    return Score

def getIntermediate(graphDatas):
    # 获取最短路径数据集合
    shortestDatas = {}
    for key in graphDatas.keys():
        shortestData = dijkstra.dijkstra(graphDatas, key)
        shortestDatas[key] = shortestData  # 三重字典。

    # 构建居间度集合
    interval = {}
    for key in graphDatas.keys():
        score = intermediaryDegreeScore(key, shortestDatas)
        interval[key] = score

    return interval

def getDensity(wordsData):
    simData, missingWord = similarity.calculationSim(wordsData)
    graphDatas = similarity.getGraph(wordsData, simData)
    interval = getIntermediate(graphDatas)

    wordCount = len(interval)    # 节点个数
    s = 10  # 初始区间个数
    c = 2   # 区间增长速度
    d = 0.1     # 区间密度阈值
    max = 6    # 区间最大划分次数


    # 按照键值排序（降序）
    sortedInterval = sorted(interval.items(), key=lambda asd: asd[1], reverse=True)
    # 获取当前居间度密度最大值
    maxratio, intervalDensity = refinementBC(sortedInterval, s)

    # 设定循环次数
    loop = 1
    while maxratio >= d and loop < max:
        s = s * c
        maxratio, intervalDensity = refinementBC(sortedInterval, s)
        loop += 1

    # 根据获取到的居间度密度集合进行相应的单词的居间度密度集合更新

    # 居间度密度集合
    intermediaryDensity = defaultdict(float)
    for key in intervalDensity:
        wordData = intervalDensity[key]
        wordList = wordData.split(',')
        wordNum = len(wordList)
        for word in wordList:
            intermediaryDensity[word] = wordNum / wordCount
    return intermediaryDensity



# 最优区间划分细度(降序排列的居间度集合)
# 计算最大居间度密度
# 参数:按居间度降序排列的居间度集合sortedInterval,区间划分个数s
def refinementBC(sortedInterval, s):
    # 顶点个数
    wordCount = len(sortedInterval)
    # 居间度最大值&最小值
    maxIntermediaryDegree = sortedInterval[0][1]
    minIntermediaryDegree = sortedInterval[wordCount - 1][1]
    # print maxIntermediaryDegree, minIntermediaryDegree
    # 居间度划分区间长度
    intervalScore = (maxIntermediaryDegree - minIntermediaryDegree) / s

    # 居间度密度
    intervalDensity = {}

    tmpNode = minIntermediaryDegree
    # 按照居间度平均划分到不同的区间内，区间键为int，键值为单词(中间使用,连接)
    for key in sortedInterval:
        flag = int((key[1] - minIntermediaryDegree) / intervalScore)
        if flag in intervalDensity:
            intervalDensity[flag] = intervalDensity.get(flag) + ',' + key[0]
        else:
            intervalDensity[flag] = key[0]

    # 首次对区间度集合进行检测,输出当前最大的居间度密度作为比较
    maxratio = 0
    for key in intervalDensity:
        wordData = intervalDensity.get(key)
        wordList = wordData.split(',')
        wordNum = len(wordList)
        if maxratio < (wordNum / wordCount):
            maxratio = (wordNum / wordCount)
    return maxratio, intervalDensity





