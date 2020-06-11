import json

def writeToTxt(filename, keywords):
    str_txt = ""
    for single_keywords in keywords:
        str_txt = str_txt + single_keywords[0] + "   " + str(single_keywords[1]) + "\n"
    with open(filename, 'w') as file_object:
        file_object.write(str_txt)


def writeToJson(filename, keywords):
    str_json = '{"keywords":['  # 储存json的字符串
    for single_keywords in keywords:
        str_json = str_json + '{"text": "' + single_keywords[0] + '","score": "' + str(single_keywords[1]) + '"},'
    str_json = str_json[:-1]
    str_json += "]}"
    data_json = json.loads(str_json)
    data_str = json.dumps(data_json, indent=4, ensure_ascii=False)
    with open(filename, 'w') as file_object:
        file_object.write(data_str)


def writeDict(filename, dicts):
    str_txt = ""
    for key, value in dicts.items():
        str_txt = str_txt + key + " " + str(value) + "\n"
    with open(filename, 'w') as file_object:
        file_object.write(str_txt)


def writeDictToJson(filename, dicts, dictName):
    str_json = '{"' + dictName + '":['
    for key, value in dicts.items():
        str_json = str_json + '{"key": "' + key + '","value": "' + str(value) + '"},'
    str_json = str_json[:-1]
    str_json += "]}"
    data_json = json.loads(str_json)
    data_str = json.dumps(data_json, indent=4, ensure_ascii=False)
    with open(filename, 'w') as file_object:
        file_object.write(data_str)