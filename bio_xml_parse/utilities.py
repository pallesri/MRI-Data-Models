#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np

import re
import itertools
import math

from scipy.spatial.distance import cdist

import nltk
from nltk.tokenize import TreebankWordTokenizer as twt

from sklearn.model_selection import train_test_split

from flair.models import SequenceTagger
from flair.data import Sentence


# **Function for finding all actor matches in the the text**

# In[3]:


def findall_actor(row):
    
    """
        row: input is row of a dataframe
        returns ['with_accurate_actor', 'accurate_actor', 'num_accurate_actor_match']
    """
    act = row['actor']

    if act is np.nan:
        return [False,np.nan, 0]
    else:
        if act[-1] in ['(', ')', ']','[']:
            #act = r'\b' + act.replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\s'
            act = r'\b' + act.replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]")
        else:
            act = r'\b' + act.replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\b'
        text = row['text']
        all_match = re.findall(act, text, re.I)
        tmp = len(all_match)
        if tmp == 0:
            return [False,np.nan, 0]
        elif len(all_match[0]) == 1:
            return [False, np.nan, 0]
        else:
            return [True,all_match[0],tmp]


# **Functions to get span of actors or hints**

# In[4]:


def get_span(row, target):
    text = row['text']
        
    if row[target][-1] in ['(', ')', ']','[']:
        p = r'\b' + row[target].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\s'
    else:
        p = r'\b' + row[target].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\b'
          
    #p = row[target].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") # replace parentheses with \) or \]
    #m = re.search(p, text, re.I)
    #p = ' '.join(p.split())
    
    m = re.search(' '.join(p.split()), text, re.I)
    return list(m.span())

# Above function just returns the span of occurance of the actor in the text. Where it starts and where it ends
# give it a dataframe and actor column name, it will add four new columns start_actor, end_actor, start_hint, end_hint
# usage ex:
# tmp[['start_actor','end_actor']] = tmp.apply(get_span, args=['actor'], axis = 1, result_type = 'expand')
# tmp[['start_hint','end_hint']] = tmp.apply(get_span, args=['hint'], axis = 1, result_type = 'expand')


# In[5]:


def get_span2(row, actor, num_actm):
    """
    row: row of a data frame
    actor: actor
    num_actm: num_accurate_actor_match
    
    returns the span of actor in the text
    comapred to the above get_span function, this function can work for multiple same actor occurances, and when we need the 
    span for only one correct actor occurence.
    """
    text = row['text']
    act = row[actor]
    #print (text)
    #print (act)
    #print ('no of actors', row[num_actm])
    
    hints = ['shall', 'will', 'must', 'is required to', 'are required to']
#     num_hints = len(re.findall(ht,text,re.I))
#     print ('no of hints', num_hints)
    
    if(row[num_actm] == 0):
        null_pos = [np.nan, np.nan]
        return null_pos
    
    elif(row[num_actm] == 1):
        if row[actor][-1] in ['(', ')', ']','[']:
            p = r'\b' + row[actor].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]")
        else:
            p = r'\b' + row[actor].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\b'
        #p = row[target].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") # replace parentheses with \) or \]
        #m = re.search(p, text, re.I)
        #p = ' '.join(p.split())
        m = re.search(p, text, re.I)
        #print (p)
        return list(m.span())
    
    else:
        if row[actor][-1] in ['(', ')', ']','[']:
            p = r'\b' + row[actor].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]")
        else:
            p = r'\b' + row[actor].replace('(', "\(").replace(')', "\)").replace('[',"\[").replace(']',"\]") + r'\b'
            
        actor_pos = [[tok.start(), tok.end()] for tok in re.finditer(p,text,re.I)]

        hint_pos = np.array([(re.search(ht,text,re.I).span()) for ht in hints if len(re.findall(ht,text,re.I)) > 0])
#         print ('actor_pos', actor_pos)
#         print ('hint pos', hint_pos)
        dist = cdist(actor_pos, hint_pos)
#         print ('dist', dist)
        return actor_pos[np.argmin(dist)]
    

# Above function just returns the span of occurance of the actor in the text. Where it starts and where it ends
# give it a dataframe and actor column name, it will add four new columns start_actor, end_actor, start_hint, end_hint
# usage ex:
# tmp[['start_actor','end_actor']] = tmp.apply(get_span, args=['actor'], axis = 1, result_type = 'expand')
# tmp[['start_hint','end_hint']] = tmp.apply(get_span, args=['hint'], axis = 1, result_type = 'expand')


# **Function to extract the statement category (p1,p2, p3,p4)**

# In[6]:


def extract_cat(ac,text):
    
    """
    ac: list of actors
    text: paragraph text
    
    returns the statement category (p1, p2, p3, p4)
    """
    
    broken_list_start = re.compile(r"([(][a-zA-Z0-9][)])|([a-zA-Z0-9]\.)")
    para = text.lower()
    all_comb = [] # all combination of actor and cv
    ht = ['shall', 'will', 'must', 'is required to', 'are required to']

    if len(ac) == 0:
        new_cat = 'p2'
    else:
        for x,y in list(itertools.product(ac, ht)):
            all_comb.append(x.replace(' ', '') + y.replace(' ', ''))
            if (para[-1] == ':') and (re.match(broken_list_start, para) is not None):
                new_cat = 'p5'
            elif any(' '.join(x.lower().split()) not in ' '.join(para.lower().split()) for x in ac):
            #elif any(x.lower() not in para for x in ac):
                new_cat = 'p4'
            elif len(all_comb) > 0:
                if any(comb.lower() in para.replace(' ', '') for comb in all_comb):
                    new_cat = 'p1'
                else:
                    new_cat = 'p3'
            else:
                new_cat = 'p6'
    return new_cat


# **Funtion to convert the data into BIO format**

# In[7]:


def extract_bio(df, tag_ls):
    """
    df: dataframe
    tag_ls: list of column names for which the tagging needs to be done ex; ['actor']. span should have already been calculated.
    
    returns bio tagged data
    """
    result = []
    for i in df.index:
        this_row = df.loc[i]
        pid = this_row['id']

        span_start, span_end = zip(*list(twt().span_tokenize(this_row['text'])))
        token, pos = zip(*nltk.pos_tag(twt().tokenize(this_row['text'])))
        token_df = pd.DataFrame({'word': token,
                                 'pos': pos,
                                'w_start':span_start,
                                'w_end':span_end})   
        #print (token_df)
        
        for name in tag_ls:
            span_tag = df[df.id == pid][['start_'+name,'end_'+name, name]]
            #print (span_tag)
            token_df = token_df.merge(span_tag, how = 'left', left_on='w_start',right_on = 'start_'+name)
            #print (token_df)
            for k in token_df[token_df['start_'+name].notnull()].index:
                token_df.at[k,name] = 'B-' + name
                end = token_df.at[k,'end_'+name]
                while token_df.at[k,'w_end'] < end :
                    k += 1
                    token_df.at[k,name] = 'I-' + name
        
        token_df = token_df[['word','pos']+tag_ls].fillna('O')
        
        result.append(token_df)
        
    return result  

# Above function takes in df, list of actor, and hint columns. 
# returns list where each element is the text paragraph where each word is tagged in bio-format
# [           word  pos    actor    hint
#  0          DoDD  NNP        O       O
#  1      4165.50E   CD        O       O
#  2             ,    ,        O       O
#  3      February  NNP        O       O
#  4             7   CD        O       O
#  5             ,    ,        O       O
#  6          2014   CD        O       O
#  7            b.   NN        O       O


# usage ex:
# tmp.reset_index(inplace=True)
# tmp_result = reprot2bio(tmp, ['actor','hint'])

# the above list of each paragrah tagged wordds in the text, can be converted into a dataframe

# tmp_concat = pd.concat(tmp_result, keys =tmp.id.to_list())  . Here the id is the paragraphd id


# **Function to split the data into train, dev, test**

# In[8]:


def train_test_dev_split(pmid, p_train = 0.7, p_test = 0.15, r1 = 42, r2 = 100):
    """
    split the id list into trian test dev list

    pmid: list list of id for this func
    p_train: train set per
    p_test: test set per
    r1: random state for first split
    r2: random state for second split

    return:
        train_pmid: list for train
        test_pmid: list for test
        dev_pmid: list for dev
    """
    train_pmid, other = train_test_split(pmid, test_size = (1 - p_train), random_state = r1)
    test_pmid, dev_pmid = train_test_split(other, test_size = p_test/(1 - p_train), random_state = r2)
    return train_pmid, test_pmid, dev_pmid

# This function just randomly splits the data into training, dev, and test


# **Function to Extract Actors from the text**

# In[9]:


def extract_actors(stext, model_name):
    ss = Sentence(stext)
    model_name.predict(ss, all_tag_prob = True)
    
    ner = ss.to_dict(tag_type='ner')
    tokens = [elem['text'] for elem in ner['entities']]
    confidence = [elem['confidence'] for elem in ner['entities']]
     
    if len(tokens) == 0:
        scores = []
        for token in ss:
            temp = {idx: token.tags_proba_dist['ner'][idx].score for idx in range(1,4)}
            scores.append(max(temp.values()))
        confidence = [min(scores)]
    
    return (tokens, confidence)


# **Function for comparing tagged actors and predicted actors for a match**

# In[10]:


def actor_match(a1,a2):
    # a1,a2 are list of actors for tagged actors, and predicted actors respectively
    
    if(len(a1) != len(a2)):
        return False
    else:
        a1 = ' '.join(a1).lower()
        a2 = ' '.join(a2).lower()
        a1 = re.sub('[^a-zA-Z0-9]', ' ', a1).strip()    # if we want to compare tagged vs. predicted by removing punctuation
        a2 = re.sub('[^a-zA-Z0-9]', ' ', a2).strip()    # if we want to compare tagged vs. predicted by removing punctuation
        return a1 == a2


# In[ ]:




