                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       # -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 19:32:15 2018

@author: TULIKA MITHAL
NetId: txm172030
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 15:27:35 2018

@author: lenovo
"""

import sys
import os
import numpy as np


# preprocess data
def preprocess(data):
    
    #extracting tags to form bigrams
    tagset = []
    
    #list of distinct tags
    tag_dist = []
    
    #count of each tag
    tag_count = {}
    
    #count of word given tag
    word_tag_count = {}
    
    #count of tags bigram
    tag_bigram = {}
 
    for line in data:
        words = []
        words = line.split(' ')
        tagset = []
        for word in words:
            word_tag = []
            word_tag = word.split('/')
            
            if word in word_tag_count:
                word_tag_count[word] += 1
            else:
                 if word != '<start>/<start>':
                     word_tag_count[word] = 1
                
            if len(word_tag) == 2:
                tagset.append(word_tag[1])
                if word_tag[1] != '<start>': 
                    if word_tag[1] in tag_count:
                        tag_count[word_tag[1]] += 1
                    else:
                        tag_dist.append(word_tag[1])
                        tag_count[word_tag[1]] = 1
                        
            else:
                tagset.append(word_tag[0])
                if word_tag[0] != '<start>': 
                    if word_tag[0] in tag_count:
                        tag_count[word_tag[0]] += 1
                    else:
                        tag_dist.append(word_tag[0])
                        tag_count[word_tag[0]] = 1
            
    
        for i in range(len(tagset)-1):
            bigram = tagset[i]+" "+tagset[i+1]
            if bigram in tag_bigram:
                tag_bigram[bigram] += 1
                        
            else:
                tag_bigram[bigram] = 1
        
  
    return tag_dist, tag_count, word_tag_count, tag_bigram
            
#################################################### START ##################################################################################           
            
# path to brown corpus folder 
path = sys.argv[1]
data = []

#reading all the files
for path,dir,files in os.walk(path):
    counter = 0
    for f in files:
        if counter<400:
            file = open(os.path.join(path,f),'r')
            for line in file:
                if len(line.strip()) > 0:
                    line = '<start>/<start> ' + line.strip()
                    data.append(line)
        counter = counter +1
                
####################################################################################################################################################

# preprocessing data           
tag_dist, tag_count, word_tag_count, tag_bigram = preprocess(data)

print(len(tag_dist))
print(len(word_tag_count))
print(len(tag_bigram))

input_observations = sys.argv[2]

words = []
words = input_observations.split()
observations_length = len(words)

viterbi = np.zeros((len(tag_dist),observations_length))
backpointer = np.zeros((len(tag_dist),observations_length))


#############################################################################################################################################################

for i in range(len(tag_dist)):
    if '<start> '+ tag_dist[i] in tag_bigram:
        if words[0]+"/"+tag_dist[i] in word_tag_count:
            viterbi[i][0] = ((tag_bigram['<start> '+ tag_dist[i]] + 0.1)/((0.1*len(tag_count))+len(data)))* ((word_tag_count[words[0]+"/"+tag_dist[i]] + 0.1)/((0.1*len(word_tag_count))+tag_count[tag_dist[i]]))
        else:
            viterbi[i][0] = ((tag_bigram['<start> '+ tag_dist[i]] + 0.1)/((0.1*len(tag_count))+len(data)))* ((0.1)/((0.1*len(word_tag_count))+tag_count[tag_dist[i]]))
    else:
        if words[0]+"/"+tag_dist[i] in word_tag_count:
            viterbi[i][0] = ((0.1)/((0.1*len(tag_count))+len(data)))* ((word_tag_count[words[0]+"/"+tag_dist[i]] + 0.1)/((0.1*len(word_tag_count))+tag_count[tag_dist[i]]))
        else:
            viterbi[i][0] = ((0.1)/((0.1*len(tag_count))+len(data)))* ((0.1)/((0.1*len(word_tag_count))+tag_count[tag_dist[i]]))

#################################################################################################################################################################        
            
            
trans_prob = {}         
for bigram in tag_bigram:
    splt = []
    splt = bigram.split()
    if len(splt) >1:
        tag = (bigram.split())[0]
        if tag in tag_count:
            trans_prob[bigram] = (tag_bigram[bigram] + 0.1)/(tag_count[tag]+(0.1*len(tag_count)))
        
prob = {}         
for word_tag in word_tag_count:
    splt = []
    splt = word_tag.split('/')
    if len(splt) >1:
        tag = (word_tag.split('/'))[1]
        if tag in tag_count:
            prob[word_tag] = (word_tag_count[word_tag]+0.1)/(tag_count[tag] + (0.1*len(word_tag_count)))


###########################################################################################################################################################  

for i in range(1,observations_length):
    for j in range(len(tag_dist)):
        max = -1;
        for k in range(len(tag_dist)):
            if tag_dist[k]+" "+tag_dist[j] in trans_prob:
                if words[i]+"/"+tag_dist[j] in prob:
                    val = (trans_prob[tag_dist[k]+" "+tag_dist[j]])*(prob[words[i]+"/"+tag_dist[j]])*viterbi[k][i-1]
                else:
                    val = (trans_prob[tag_dist[k]+" "+tag_dist[j]])*(0.1/(tag_count[tag_dist[j]] + (0.1*len(word_tag_count))))*viterbi[k][i-1]                   
            else:
                if words[i]+"/"+tag_dist[j] in prob:
                    val = (0.1/(tag_count[tag_dist[j]]+(0.1*len(tag_count))))*(prob[words[i]+"/"+tag_dist[j]])*viterbi[k][i-1]
                else:
                    val = (0.1/(tag_count[tag_dist[j]]+(0.1*len(tag_count))))*(0.1/(tag_count[tag_dist[j]] + (0.1*len(word_tag_count))))*viterbi[k][i-1]
             
            if val>max:
                max = val
                max_state = k
        
        viterbi[j][i] = max
        backpointer[j][i] = max_state
        
##################################################################################################################################################################
        
        
ans=''     
max = -1   
max_state = -1
for i in range(len(tag_dist)):
    if (viterbi[i][observations_length-1]) > max:
        max_state = i
        max = viterbi[i][observations_length-1]
        ans = words[observations_length-1]+"/"+tag_dist[i]
        
       
backpointer = backpointer.astype(int)


for i in range(1,observations_length):
    ans =  words[observations_length-i-1]+"/"+(tag_dist[backpointer[max_state][observations_length-i]])+" "+ans
    max_state = backpointer[max_state][observations_length-i]
  
   
print("Tagged sentence")   
print(ans)