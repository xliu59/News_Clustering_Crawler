#!/bin/bash

cd ./final/spiders/
rm -f news.json

python3 auto.py

cp news.json ../../PDF_Generator/

cd ../../crawler2/

rm -f crawler.db

python run.py

cp res.json ../PDF_Generator/

cd ../token/

python3 token.py
python3 my_tokenize.py articles.raw
perl make_hist.prl < articles.tokenized > articles.tokenized.hist

cd ../similarity/

python3 compute.py

cd ../from_list_to_dict/

python3 toDict.py

cd ../PDF_Generator/

python3 entry.py