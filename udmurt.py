import re
import json

def read_file(file):
    f = open(file, 'r', encoding='utf-8')
    s = str(f.read())
    f.close()
    return s

def make_dict(s):
    d = {}
    s = s.split('\n\n')
    lex = 'lex: (.+?)\n'
    gramm = 'gramm: (.+?)\n'
    trans = 'trans_ru: (.+)'

    for i in s:
        res1 = re.search(lex, i)
        res1 = res1.group(1)
        res2 = re.search(gramm, i)
        res2 = res2.group(1)
        res3 = re.search(trans, i)
        if res3:
            res3 = res3.group(1)
        else:
            res3 = 'перевод отсутствует'
        cort = (res2, res3)
        d[res1] = cort
    return d

def make_json(d, file):
    s = json.dumps(d, sort_keys=True, ensure_ascii = False)
    file = open(file, "w", encoding = "utf-8")
    file.write(s)
    file.close()

if __name__ == '__main__':
    make_json(make_dict(read_file('ADJ.txt')),'result.txt')
    
