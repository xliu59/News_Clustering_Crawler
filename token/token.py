# -*- coding: utf-8 -*-
import json

with open('../final/spiders/news.json') as json_file:
    data1 = json.load(json_file)

    stemmed_data1 = [x for x in data1 if x['headline'] is not None]

    #for i in range(len(stemmed_data)):
    #    json_file.write(".I " + str(i))
    #    json_file.write(stemmed_data[i]['headline'])

with open('../crawler2/res.json') as json_file:
    data2 = json.load(json_file)

    stemmed_data2 = [x for x in data2 if x['headline'] is not None]

stemmed_data = stemmed_data1 + stemmed_data2


fo = open('articles.raw', 'w+')

for i in range(len(stemmed_data)):
	fo.write('\n.I ' + str(i + 1) + '\n')
	fo.write('.T\n')
	fo.write(stemmed_data[i]['headline'] + '\n')

fo.close()


fo = open('articles.titles', 'w+')

for i in range(len(stemmed_data)):
    if i < 9:
        fo.write(str(i + 1) + '    #  ' + stemmed_data[i]['headline'] + '\n')
    else:
        fo.write(str(i + 1) + '   #  ' + stemmed_data[i]['headline'] + '\n')

fo.close()


for i in range(len(stemmed_data)):
    stemmed_data[i]['number'] = str(i + 1)

with open('total.json', 'w+') as json_file:
    json_file.write(json.dumps(stemmed_data))