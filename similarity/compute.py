#!/usr/bin/env python
import re
import os
import math
from collections import defaultdict
import json

############################################################
## Program Defaults and Global Variables
############################################################
#DIR, file_name = os.path.split(os.path.realpath(__file__))
HOME = "../token"

token_docs = HOME + "/articles.tokenized"        # tokenized cacm journals
corps_freq = HOME + "/articles.tokenized.hist"   # frequency of each token in the journ.
stoplist = HOME + "/common_words"                # common uninteresting words
titles = HOME + "/titles.articles"               # titles of each article in cacm

doc_vector = []
qry_vector = []
docs_freq_hash = defaultdict(int)
corp_freq_hash = defaultdict(int)
stoplist_hash = set()
doc_simula = []
res_vector = []

##########################################################
##  INIT_FILES
##########################################################

def init_files(): 
    global token_docs
    global corps_freq 
    global stoplist
    global token_intr 
    global inter_freq

##########################################################
##  INIT_CORP_FREQ
##
##  This function reads in corpus and document frequencies from
##  the provided histogram file for both the document set
##  and the query set. This information will be used in
##  term weighting.
##
##  It also initializes the arrays representing the stoplist,
##  title list and relevance of document given query.
##########################################################

def init_corp_freq(): #
    for line in open(corps_freq, 'r'):
        per_data = line.strip().split()
        if len(per_data) == 3:
            corp_freq, doc_freq, term = line.strip().split()
            docs_freq_hash[term] = int(doc_freq)
            corp_freq_hash[term] = int(corp_freq)

    for line in open(stoplist, 'r'):
        if line:
            stoplist_hash.add(line.strip())


##########################################################
##  INIT_DOC_VECTORS
##
##  This function reads in tokens from the document file.
##  When a .I token is encountered, indicating a document
##  break, a new vector is begun. When individual terms
##  are encountered, they are added to a running sum of
##  term frequencies. To save time and space, it is possible
##  to normalize these term frequencies by inverse document
##  frequency (or whatever other weighting strategy is
##  being used) while the terms are being summed or in
##  a posthoc pass.  The 2D vector array
##
##    doc_vector[ doc_num ][ term ]
##
##  stores these normalized term weights.
##
##  It is possible to weight different regions of the document
##  differently depending on likely importance to the classification.
##  The relative base weighting factors can be set when
##  different segment boundaries are encountered.
##
##  This function is currently set up for simple TF weighting.
##########################################################

def init_doc_vectors(): #
    doc_num = 0
    global total_docs

    TITLE_BASE_WEIGHT = 4     # weight given a title token
    KEYWD_BASE_WEIGHT = 3     # weight given a key word token
    ABSTR_BASE_WEIGHT = 1     # weight given an abstract word token
    AUTHR_BASE_WEIGHT = 4     # weight given an an author token

    BASE_WEIGHT = {".T" : TITLE_BASE_WEIGHT, ".K" : KEYWD_BASE_WEIGHT,\
                    ".W" : ABSTR_BASE_WEIGHT, ".A" : AUTHR_BASE_WEIGHT}

    tweight = 0
    # push one empty value onto qry_vectors so that
    # indices correspond with query numbers
    doc_vector.append(defaultdict(int))

    for word in open(token_docs, 'r'):
        word = word.strip()
        if not word or word == ".I 0":
            continue  # Skip empty line

        if word[:2] == ".I":
            new_doc_vec = defaultdict(int)
            doc_vector.append(new_doc_vec)
            doc_num += 1
        elif word in BASE_WEIGHT:
            tweight = BASE_WEIGHT[word]
        elif word not in stoplist_hash and re.search("[a-zA-Z]", word):
            if docs_freq_hash[word] == 0:
                print ("no hash:", word)
                exit("ERROR: Document frequency of zero: " + word + \
                     " (check if token file matches corpus_freq file\n")
            new_doc_vec[word] += tweight

    total_docs = doc_num



###############################################################
##  INIT_QRY_VECTORS
##
##  This function should be nearly identical to the step
##  for initializing document vectors.
##
##  This function is currently set up for simple TF weighting.
###############################################################
def init_qry_vectors(): #
    global total_qrys
    qry_vector = doc_vector
    total_qrys = total_docs


###########################################################
## GET_RETRIEVED_SET
##
##  Parameters:
##
##  my_qry_vector    - the query vector to be compared with the
##                  document set. May also be another document
##                  vector.
##
##  This function computes the document similarity between the
##  given vector "my_qry_vector" and all vectors in the document
##  collection storing these values in the array "doc_simula"
##
##  An array of the document numbers is then sorted by this
##  similarity function, forming the rank order of documents
##  for use in the retrieval set.
##
##  The similarity will be
##  sorted in descending order.
##########################################################

def get_retrieved_set():#
    # "global" variable might not be a good choice in python, but this
    # makes us consistant with original perl script
    global doc_simila, res_vector

    tot_number = len(doc_vector) 

    doc_simila = {}   # insure that storage vectors are empty before we
    res_vector = []   # calculate vector similarities
    for i in range(1, tot_number):
        temp_simila = {}
        i_total_sim = 0
        for j in range (1, tot_number):
            sim_i_j = cosine_sim_a(doc_vector[i], doc_vector[j])
            if sim_i_j == 0:
                continue
            temp_simila[j] = sim_i_j
            i_total_sim += sim_i_j
        temp_simila["total"] = i_total_sim + 0.1
        sorted_temp_simila = sorted(temp_simila.items(), key=lambda d:d[1], reverse = True)
        doc_simila[i] = sorted_temp_simila
        #doc_simila = sorted(doc_simila, reverse=True)
    sorted_doc_simila = sorted(doc_simila.items(), key=lambda d:d[1], reverse = True)

    #remove duplication
    flag_array = []
    for i in range(0, tot_number):
        flag_array.append(None) 
    for (doc_x, ranks_to_x) in sorted_doc_simila:
        temp_doc = []
        if flag_array[doc_x] != None: # this doc has already been related by other docs
            continue
        else:
            temp_doc.append(doc_x)
            flag_array[doc_x] = 1
        for (doc_y, sim) in ranks_to_x:
            if doc_y == 'total' or flag_array[doc_y] != None or len(temp_doc) == 3:
                continue
            else:
                temp_doc.append(doc_y)
                flag_array[doc_y] = 1
        res_vector.append(temp_doc)

    print (json.dumps(res_vector))
    with open('list.json', 'w') as outfile:
        outfile.write(json.dumps(res_vector))

########################################################
## COSINE_SIM_A
##
## Computes the cosine similarity for two vectors
## represented as associate arrays. You can also pass the
## norm as parameter
##
## Note: You may do it in a much efficient way like
## precomputing norms ahead or using packages like
## "numpy", below provide naive implementation of that
########################################################

def cosine_sim_a(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0): #
    if not vec1_norm:
        vec1_norm = sum(v * v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v * v for v in vec2.values())

    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return cross_product / math.sqrt(vec1_norm * vec2_norm)

########################################################
##  COSINE_SIM_B
##  Same thing, but to be consistant with original perl
##  script, we add this line
########################################################
#def cosine_sim_b(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
#    return cosine_sim_a(vec1, vec2, vec1_norm, vec2_norm)

########################################################
##  DICE_SIM
##  for part b
########################################################
#def dice_sim(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
#    if not vec1_norm:
#        vec1_norm = sum(v for v in vec1.values())
#    if not vec2_norm:
#        vec2_norm = sum(v for v in vec2.values())
#
#    # save some time of iterating over the shorter vec
#    if len(vec1) > len(vec2):
#        vec1, vec2 = vec2, vec1
#
#    # calculate the cross product
#    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
#    return 2 * cross_product / (vec1_norm + vec2_norm)


########################################################
##  JACCARD_SIM
##  for part b
########################################################
#def jaccard_sim(qry_vector, doc_vector):
#    num = 0
#    sum_1 = 0
#    sum_2 = 0
#    qry_size = len(qry_vector)
#    doc_size = len(doc_vector)
#
#    #if query_vector is longer, make it the shorter one
#    if qry_size > doc_size:
#        temp = qry_vector
#        qry_vector = doc_vector
#        doc_vector = temp
#    
#    #calculate the cross product
#    for key, value in qry_vector.items():
#        num += value * (doc_vector[key] or 0)
#
#    #calculate the sum of squares
#    for i in range(0, qry_size):
#        sum_1 += i
#    for i in range(0, doc_size):
#        sum_2 += i
#    return (num / (sum_1 + sum_2 - num))

########################################################
##  OVERLAP_SIM
##  for part b
########################################################
#def overlap_sim(qry_vector, doc_vector):
#    num = 0
#    sum_1 = 0
#    sum_2 = 0
#    qry_size = len(qry_vector)
#    doc_size = len(doc_vector)
#
#    #if query_vector is longer, make it the shorter one
#    if qry_size > doc_size:
#        temp = qry_vector
#        qry_vector = doc_vector
#        doc_vector = temp
#    
#    #calculate the cross product
#    for key, value in qry_vector.items():
#        num += value * (doc_vector[key] or 0)
#
#    #calculate the sum of squares
#    for i in range(0, qry_size):
#        sum_1 += i
#    for i in range(0, doc_size):
#        sum_2 += i
#    return (num / min(sum_1, sum_2))



#if __name__ == "__main__":
init_files()
init_corp_freq()
init_doc_vectors()
init_qry_vectors()
get_retrieved_set()


