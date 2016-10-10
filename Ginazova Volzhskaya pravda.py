import re
import urllib.request
import html
import os
import time


#директория для газеты
def beginwithpaperdir(papername):
    if not os.path.exists(papername):
        os.makedirs(papername)
    os.chdir(papername)    


#директории для разных типов текстов    
def makedirectories():
    if not os.path.exists('plain'):
        os.makedirs('plain')
    if not os.path.exists('mystem-xml'):
        os.makedirs('mystem-xml')
    if not os.path.exists('mystem-plain'):
        os.makedirs('mystem-plain')


#преобразование текста сначала в читаемый, а потом в красивый вид
def cleartext(text):
    regTag = re.compile('<.*?>', flags=re.U | re.DOTALL)
    regScript = re.compile('<script>.*?</script>', flags=re.U | re.DOTALL)
    regComment = re.compile('<!--.*?-->', flags=re.U | re.DOTALL)
    text = regScript.sub("", text)
    text = regComment.sub("", text)
    text = regTag.sub("", text)
    text = html.unescape(text)
    text = re.sub('\t+','',text)
    text = re.sub('  +', ' ',text)
    text = re.sub('\r\n','\n',text)
    text = re.sub('\n +','\n',text)
    text = re.sub('\n\n+','\n',text)
    text = re.sub('^ ?\n?','',text)
    text = re.sub('\n$','',text)
    return text


#преобразование даты из строки с месяцем-словом в нужный формат + получение отдельно месяца и года
def getnormaldate(strdate):
    monthsw = ['','Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    month = monthsw.index(strdate[3:-5])
    year = strdate[-4:]
    date = strdate[:2]+'.'+"%02d"%(month)+'.'+year
    return date,month,year


#кроулер
def collect(beginning):
    metafile = open('metadata.csv','a',encoding='utf-8')
    
    #шапка csv-таблицы
    metafile.write('path\tauthor\tsex\tbirthday\theader\tcreated\tsphere\tgenre_fi\ttype\ttopic\tchronotop\tstyle\taudience_age\taudience_level\taudience_size\tsource\tpublication\tpublisher\tpubl_year\tmedium\tcountry\tregion\tlanguage\n')
    #шаблоны для дальнейшего заполнения
    row = '%s\t%s\t\t\t%s\t%s\tпублицистика\t\t\t%s\t\tнейтральный\tн-возраст\tн-уровень\tгородская\t%s\tВолжская правда\t\t%s\tгазета\tРоссия\tВолгоградская область\tru'
                                                                                                        #путь к чистому файлу, автор, название, дата, категория, url, год
    meta = '@au %s\n@ti %s\n@da %s\n@topic %s\n@url %s' #автор, название, дата, категория, url

    #регулярные выражения для поиска нужной информации и самой статьи
    findtext = re.compile('<!-- Item introtext -->(.*?)<!-- Item Rating -->',flags=re.DOTALL)
    findauth = re.compile('<span class="itemAuthor">.*?Автор&nbsp;(.*?)</span>',flags=re.DOTALL)
    findtitle = re.compile('<h2 class="itemTitle">(.*?)</h2>',flags=re.DOTALL)
    finddate = re.compile('<span class="itemDateCreated">.*?, (.*?) \d\d:',flags=re.DOTALL)
    findcat = re.compile('<div class="itemCategory">.*?</span>(.*?)</div>',flags=re.DOTALL)

    #ищем последнюю статью на сайте, чтобы определить, до какого номера перебирать номера статей
    mainpage = urllib.request.urlopen('http://gazeta-vp.ru').read().decode('utf-8')
    lastitem = int(re.findall('<div class="latestItemList">.*?<h2 class="latestItemTitle">.*?<a href="/news/.+?item/(.*?)-',mainpage,flags=re.DOTALL)[0])

    #пытаемся поймать статью по номеру страницы на сайте
    for i in range(beginning,lastitem+1): #с задаваемой извне начальной точки до самой свежей статьи
        try:
            url = 'http://gazeta-vp.ru/news/item/'+str(i)
            page = urllib.request.urlopen(url).read().decode('utf-8')
        except:
            continue

        #ищем всё по скомпилированным регулярным выражениям
        text = cleartext((findtext.findall(page)+[''])[0])
        author = cleartext((findauth.findall(page)+[''])[0])
        title = cleartext((findtitle.findall(page)+[''])[0])
        date,month,year = getnormaldate(cleartext((finddate.findall(page)+[''])[0]))
        category = cleartext((findcat.findall(page)+[''])[0])
        
        #кладем статью в нужную папку
        path = 'plain'+os.sep+str(year)+os.sep+str(month)
        if not os.path.exists(path):
            os.makedirs(path)
            lastnum = 0
        else:
            lastnum = sorted(list(map(lambda x: int(x[:-4]),os.listdir(path))))[-1] #определяем порядковый номер последней статьи в папке
        filename = str(lastnum+1)+'.txt'
        pathtofile = path+os.sep+filename
        f = open(pathtofile,'w',encoding='utf-8')
        metafile.write(row % (pathtofile, author, title, date, category, url, year) + '\n') #пишем строку в metadata.csv

        #пишем метаданные перед текстом в файле
        if author == '':
            author = 'Noname'
        f.write('\n'.join([meta % (author, title, date, category, url), text]))
        f.close()
    metafile.close()


#удалить метаданные из файла с размеченным текстом
def deletemeta(name,regexp):
    j = open(name,'r',encoding='utf-8')
    text = j.read()
    j.close()
    new_text = re.sub(regexp,'',text,flags=re.DOTALL)
    j = open(name,'w',encoding='utf-8')
    j.write(new_text)
    j.close()


#прогон через mystem
def parse():
    os.chdir('.')
    for year in os.listdir('plain'):
        for month in os.listdir('plain'+os.sep+year):
            pathplain = 'mystem-plain'+os.sep+year+os.sep+month
            if not os.path.exists(pathplain):
                os.makedirs(pathplain)
            pathxml = 'mystem-xml'+os.sep+year+os.sep+month
            if not os.path.exists(pathxml):
                os.makedirs(pathxml)
            for f in os.listdir('plain'+os.sep+year+os.sep+month):
                os.system('C:\mystem.exe '+'plain'+os.sep+year+os.sep+month+os.sep+f+' '+pathplain+os.sep+f+' -dic') #Путь к mystem как в семинарском скрипте
                deletemeta(pathplain+os.sep+f,'^.*?\{item\?\?\}.*?\n')
                os.system('C:\mystem.exe '+'plain'+os.sep+year+os.sep+month+os.sep+f+' '+pathxml+os.sep+f[:-4]+'.xml'+' -dic --format xml')
                deletemeta(pathxml+os.sep+f[:-4]+'.xml','^.*?<w>item</w>.*?\n')


#основная функция
def wholeprocess():
    beginwithpaperdir('Volzhskaya pravda') #собственная папка для газеты, которая далее считается корнем
    makedirectories()
    collect(9500) #не вся газета, а ок.1000 последних статей (ок.168000 слов). Можно и всю газету (по состоянию на 10.10.2016 - ок.10500 потенциальных страниц)
    parse()


wholeprocess()
