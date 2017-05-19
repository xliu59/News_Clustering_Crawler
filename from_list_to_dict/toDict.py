import json

# data1 = []
# i = 0
# while i < 21:
# 	temp = []
# 	for j in range(3):
# 		i += 1
# 		temp.append(i)
# 	data1.append(temp)

# print(data1)

with open('../similarity/list.json') as json_file:
    data1 = json.load(json_file)

with open('../token/total.json') as json_file:
    data2 = json.load(json_file)

result = []
for i in range(len(data1)):
	temp = {}
	for k in range(len(data2)):
		if str(data1[i][0]) == data2[k]['number']:
			temp['headline'] =  data2[k]['headline']
			temp['image'] = data2[k]['image']
			temp['link'] = data2[k]['link']
		elif len(data1[i]) > 1 and str(data1[i][1]) == data2[k]['number']:
			temp['related_link1'] = data2[k]['link']
		elif len(data1[i]) > 2 and str(data1[i][2]) == data2[k]['number']:
			temp['related_link2'] = data2[k]['link']
	result.append(temp)

with open('show.json', 'w+') as json_file:
	json_file.write(json.dumps(result))
