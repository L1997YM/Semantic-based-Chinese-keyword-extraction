import chardet

def readFile(inputPath):
    f = open(inputPath, 'rb')
    lines = f.readlines()
    line = lines[0]
    line = line.strip()
    f_charInfo = chardet.detect(line)
    title = line.decode(f_charInfo['encoding'])

    body = ""
    for line in lines[1:]:
        line = line.strip()
        if line == b'':
            continue
        f_charInfo = chardet.detect(line)
        f_read_decode = line.decode(f_charInfo['encoding'])
        if f_read_decode != "":
            body += f_read_decode

    return title, body
