# -*- coding: utf-8 -*-
import json

def store(data, file_name):
    with open(file_name, 'w') as json_file:
        json_file.write(json.dumps(data))

def load(file_name):
    with open(file_name) as json_file:
        data = json.load(json_file)
        return data
