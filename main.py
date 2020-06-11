# !/usr/bin/python3
# -*- coding: utf-8 -*-

import uploadFile
import textPrecessing
import statistics
import outPut

import intermediate
from collections import defaultdict
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "2"


import sys
from PyQt5.QtGui import QFont
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *



# 归一化
def normalized(wordsData, dict):
    minWord = min(dict, key=dict.get)
    minValue = dict[minWord]
    maxWord = max(dict, key=dict.get)
    maxValue = dict[maxWord]
    diff = maxValue - minValue
    for word in wordsData:
        dict[word] = (dict[word] - minValue) / diff
    return dict

# 计算词语得分
def calculateScore(wordsData, interDensity, wordsLoc, wordsTfidf, wordsFlagWeight):
    score = defaultdict(float)
    sW = 0.5
    Tw = 0.5
    posW = 0.4
    locW = 1
    tfidfW = 1
    for word in wordsData:
        score[word] = sW * interDensity[word] + Tw * (
                posW * wordsFlagWeight[word] + locW * wordsLoc[word] + tfidfW * wordsTfidf[word])

    return score


def getFileName(path):
    file_name = os.path.basename(path)
    file_path = os.path.dirname(path)
    return file_name, file_path

# 处理前后继关系
def addWord(interDensity, wordsData, wordsFlagDict, nextDict, nextWordSum, preDict, preWordSum):
    for word1 in nextDict:
        if nextWordSum[word1] > 2:
            for word2 in nextDict[word1]:
                if word1 in preDict[word2] and nextDict[word1][word2] / nextWordSum[word1] >= 0.8 and preDict[word2][word1] / preWordSum[word2] >= 0.8:
                    strs = word1 + word2
                    wordsData.append(strs)
                    interDensity[strs] = max(interDensity[word1], interDensity[word2])
                    wordsFlagDict[strs] = wordsFlagDict[word2]
    return interDensity, wordsData, wordsFlagDict

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()  # 界面绘制交给InitUi方法

    def initUI(self):

        # QGridLayout() 页面布局
        grid = QGridLayout()
        self.setLayout(grid)
        # 调整布局间隔
        grid.setSpacing(20)

        # 设置五个按钮
        names = ['导入文档', '预处理', '提取语义特征', '提取统计特征', '计算词语得分']
        positions = [(0, j) for j in range(5)]
        for position, name in zip(positions, names):
            #if name == '':
            #    continue
            button = QPushButton(name)  # 创建按钮
            button.setObjectName(name)  # 设置名称（id）
            button.setEnabled(False)    # 设置按钮是否有效
            button.clicked.connect(self.on_click)   # 将按钮的点击事件链接到on_click()
            grid.addWidget(button, *position)   # 将按钮加入到布局grid中

        self.findChild(QPushButton, "导入文档").setEnabled(True)  # findChild()可以根据类型和名称找到对应的组件

        # 设置五个文本框对处理过程进行反馈
        positions = [1, 2, 3, 4, 5]
        for i, name in zip(positions, names):
            label = QLabel("")  # 创建一个标签（一个文本显示框）
            label.setObjectName(name)   # 设置名称
            label.setAlignment(Qt.AlignCenter)  # 设置居中
            grid.addWidget(label, i, 0, 1, 5)   # 把label加入布局grid中

        # 设置查看按钮
        button = QPushButton('查看')
        button.setObjectName('查看')
        button.setEnabled(False)
        button.clicked.connect(self.on_click)
        grid.addWidget(button, 7, 2, 1, 1)

        self.resize(1000, 600)  # 窗口大小
        self.center()   # 窗口居中
        self.setWindowTitle('中文关键词提取')
        self.show()

    # 窗口居中
    def center(self):

        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 按钮点击事件
    def on_click(self):
        sender = self.sender()  # 返回点击来源，为了得知哪个按钮被点击
        ButtonName = sender.text()  # 获得这个按钮上的文本
        if ButtonName == "导入文档":
            # 选择文件上传，openfile_name[0]为文件路径
            openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'txt files(*.txt)')
            if openfile_name[0] == "":
                return

            global FileName, FilePath, body, title, text
            title, body = uploadFile.readFile(openfile_name[0]) # 读取文件
            text = title + "。" + body

            # 创建输出文件目录
            FileName, FilePath = getFileName(openfile_name[0])  #将路径解析为文件名和文件夹路径
            FileName = FileName[0:-4]
            outPutPath = FilePath + "\\" + FileName + "_output"
            isExists = os.path.exists(outPutPath)
            if not isExists:
                outPutPath_s = outPutPath + "\\预处理"
                os.makedirs(outPutPath_s)
                outPutPath_s = outPutPath + "\\语义特征"
                os.makedirs(outPutPath_s)
                outPutPath_s = outPutPath + "\\统计特征"
                os.makedirs(outPutPath_s)
                outPutPath_s = outPutPath + "\\词语得分"
                os.makedirs(outPutPath_s)

            # 修改各个按钮的属性和各个标签的文本
            self.findChild(QLabel, "导入文档").setText("导入成功！文件路径：" + openfile_name[0])
            self.findChild(QLabel, "预处理").setText("")
            self.findChild(QLabel, "提取语义特征").setText("")
            self.findChild(QLabel, "提取统计特征").setText("")
            self.findChild(QLabel, "计算词语得分").setText("")
            self.findChild(QPushButton, "预处理").setEnabled(True)
            self.findChild(QPushButton, "查看").setEnabled(True)
            self.findChild(QPushButton, "提取语义特征").setEnabled(False)
            self.findChild(QPushButton, "提取统计特征").setEnabled(False)
            self.findChild(QPushButton, "提取语义特征").setEnabled(False)
            self.findChild(QPushButton, "计算词语得分").setEnabled(False)

        elif ButtonName == "预处理":
            self.findChild(QLabel, "预处理").setText("正在处理！")
            self.findChild(QPushButton, "预处理").setEnabled(False)
            QApplication.processEvents()
            global wordsData, wordsFlagDict, firstSentence, lastSentence, nextDict, nextWordSum, preDict, preWordSum
            wordsData, wordsFlagDict, firstSentence, lastSentence, nextDict, nextWordSum, preDict, preWordSum = textPrecessing.word_segmentation(body, title)

            outPutPath = FilePath + "\\" + FileName + "_output\\预处理\\wordsData.txt"

            str_txt = ""
            for word in wordsData:
                str_txt = str_txt + word + "\n"
            with open(outPutPath, 'w') as file_object:
                file_object.write(str_txt)

            outPutPath = FilePath + "\\" + FileName + "_output\\预处理\\wordsFlagDict.txt"
            outPut.writeDict(outPutPath, wordsFlagDict)
            outPutPath = FilePath + "\\" + FileName + "_output\\预处理\\wordsFlagDict.json"
            outPut.writeDictToJson(outPutPath, wordsFlagDict, 'wordsFlagDict')

            self.findChild(QLabel, "预处理").setText("预处理已完成！")
            self.findChild(QPushButton, "提取语义特征").setEnabled(True)

        elif ButtonName == "提取语义特征":
            self.findChild(QLabel, "提取语义特征").setText("正在处理！")
            self.findChild(QPushButton, "提取语义特征").setEnabled(False)
            QApplication.processEvents()
            global interDensity
            interDensity = intermediate.getDensity(wordsData)
            QApplication.processEvents()
            # 处理前后继关系
            interDensity, wordsData, wordsFlagDict = addWord(interDensity, wordsData, wordsFlagDict, nextDict,
                                                             nextWordSum, preDict, preWordSum)
            outPutPath = FilePath + "\\" + FileName + "_output\\语义特征\\interDensity.txt"
            outPut.writeDict(outPutPath, interDensity)
            outPutPath = FilePath + "\\" + FileName + "_output\\语义特征\\interDensity.json"
            outPut.writeDictToJson(outPutPath, interDensity, 'interDensity')

            self.findChild(QLabel, "提取语义特征").setText("提取语义特征已完成！")
            self.findChild(QPushButton, "提取统计特征").setEnabled(True)

        elif ButtonName == "提取统计特征":
            self.findChild(QLabel, "提取统计特征").setText("正在处理！")
            self.findChild(QPushButton, "提取统计特征").setEnabled(False)
            QApplication.processEvents()
            global wordsLoc, wordsFlagWeight, wordsTfidf
            wordsTfidf = statistics.getTfidf(len(wordsData), text)
            wordsLoc = statistics.getLoc(wordsData, wordsTfidf, title, firstSentence, lastSentence)
            wordsFlagWeight = statistics.getFlag(wordsFlagDict, wordsData)

            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsTfidf.txt"
            outPut.writeDict(outPutPath, wordsTfidf)
            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsTfidf.json"
            outPut.writeDictToJson(outPutPath, wordsTfidf, 'wordsTfidf')
            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsLoc.txt"
            outPut.writeDict(outPutPath, wordsLoc)
            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsLoc.json"
            outPut.writeDictToJson(outPutPath, wordsLoc, 'wordsLoc')
            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsFlagWeight.txt"
            outPut.writeDict(outPutPath, wordsFlagWeight)
            outPutPath = FilePath + "\\" + FileName + "_output\\统计特征\\wordsFlagWeight.json"
            outPut.writeDictToJson(outPutPath, wordsFlagWeight, 'wordsFlagWeight')

            self.findChild(QLabel, "提取统计特征").setText("提取统计特征已完成！")
            self.findChild(QPushButton, "计算词语得分").setEnabled(True)

        elif ButtonName == "计算词语得分":
            self.findChild(QPushButton, "计算词语得分").setEnabled(False)
            QApplication.processEvents()
            interDensity = normalized(wordsData, interDensity)
            wordsTfidf = normalized(wordsData, wordsTfidf)
            wordsLoc = normalized(wordsData, wordsLoc)
            score = calculateScore(wordsData, interDensity, wordsLoc, wordsTfidf, wordsFlagWeight)
            score = sorted(score.items(), key=lambda d: d[1], reverse=True)

            outPutPath = FilePath + "\\" + FileName + "_output\\词语得分\\score.txt"
            outPut.writeToTxt(outPutPath, score)
            outPutPath = FilePath + "\\" + FileName + "_output\\词语得分\\score.json"
            outPut.writeToJson(outPutPath, score)

            keywords = score[0:10]
            outPutPath = FilePath + "\\" + FileName + "_output\\词语得分\\keywords.txt"
            outPut.writeToTxt(outPutPath, keywords)
            outPutPath = FilePath + "\\" + FileName + "_output\\词语得分\\keywords.json"
            outPut.writeToJson(outPutPath, keywords)

            strs = "关键词： "
            for single_keywords in keywords:
                strs = strs + single_keywords[0] + ", "
            strs = strs[0:-2]

            self.findChild(QLabel, "计算词语得分").setText(strs)

        elif ButtonName == "查看":
            # 打开文件夹展示
            os.system("start explorer " + os.path.normpath(FilePath) + "\\" + FileName + "_output")


if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())