import sys
import re

file_name = sys.argv[1]
f = open(file_name)
lines = f.readlines()
f.close()

res_list = []
for line in lines:
	if not re.match("^\.(I [0-9]+|T)$", line):
#		print line
		line = line.lower()
		line = re.sub(r"[ ]+", " ", line)
		line = line.split()
		for word in line:
			if word not in ('', ' ','\n'):
#		words = line.split(' ')
#		print line
				res_list.append(word)
	else:
		line = re.sub(r"\n", "", line)
		res_list.append(line)			
#print res_list

with open("articles.tokenized", "w") as out_f:
	out_f.write("\n".join(res_list))
	out_f.write("\n")