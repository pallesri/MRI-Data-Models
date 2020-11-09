# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:08:12 2020

@author: Qinxin Xu
"""
from pathlib import Path
import configparser
import os
import re
import json
import shutil
import logging
import numpy as np
import pdfplumber
import random
import time
# start_time = time.time()
# time.time() - start_time
from flair.models import SequenceTagger
from flair.data import Sentence
from segtok.segmenter import split_single


def readable_pdf_to_txt(file, save_flag = 0, save_folder = 0):
    """
    transfer the readable pdf file into raw text

    file: file path
    save_flag: 1, save to path

    return: raw text string
    """
    if file.suffix != '.pdf':
        raise NameError('not pdf file')

    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tmp = page.extract_text(x_tolerance=0.2)
            if tmp is not None:
                text.append(tmp)
    if save_flag == 1:
        tmp = '\n'.join(text)
        with open(Path(save_folder)/(file.stem+'.txt'), 'w') as f:
            f.write(tmp)

    if len(text) == 0:
        raise NameError('nothing transferred')
    else:
        return '\n'.join(text)


def split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt, save_name = 0, save_flag = 0, save_folder = 0):
    """
    pp: page pattern
    header_lang: header words pattern
    normal_lang: normal language pattern
    hp_list: header pattern list
    match_set: match term set
    rawtxt: raw text
    """
    # clean the raw text
    rawtxt = re.sub(normal_lang, '', rawtxt)
    
    pos = [] # get the header position list
    match_len = [] # get the number match header
    match_hp = [] # get the match header list
    result = [] # output
    danger = ['past medical/surgical history', 'past medical history', 'past medical/surgical history']
    after_danger = ['diagnoses', 'physical exam', 'tests','diagnosis']
    
    danger4 = ['orders']
    after_danger4 = ['lab orders', 'orders','physical exam']
    
    danger2 = ['plan', 'assessment / plan', 'assessment and plan', 'assessment plan', 'primary diagnosis',
              'assessment plan']
    after_danger2 = ['medications', 'procedures', 'prescriptions', 'orders', 'vaccines', 'immunization',
                    'recommendations']
    
    danger3 = ['physical examination','physical exam','objective','physical findings']
    after_danger3 = ['vital signs']
    
    danger5 = ['assessment', 'diagnosis']
    after_danger5 = ['diagnosis', 'orders']
    
    danger6 = ['completed orders this encounter']
    after_danger6 = ['treatment']
    
    danger7=['history of present illness', 'hpi']
    after_danger7 = ['advanced care planning', 'diagnosis', 'interval history', 'interim history','fh']
    
    danger8 = ['therapy', 'current meds']
    after_danger8 = ['therapy']
    
    danger9 = ['patient instructions']
    after_danger9 = ['vaccines']
    
    danger10 = ['preventive', 'preventive medicine']
    after_danger10 = ['immunizations', 'advanced care planning', 'assessment']
    
    danger11 =['family history', 'problems']
    after_danger11 = ['problems']
    
    danger12 = ['subjective', 'current medication', 'past medical history']
    after_danger12 = ['allergy', 'allergies']
    
    danger13 = ['plan']
    after_danger13 = ['ap', 'plan', 'a/p']
    
    danger14 = ['tests', 'impression']
    after_danger14 = ['impression']
    
    danger15 = ['diagnosis', 'impression and plan']
    after_danger15 = ['diagnosis']
    
    danger16 = ['examination']
    after_danger16 = ['exam']
    
    
    # match raw text with multiple header patterns and find the best one
    for hp in hp_list:
        header = []
        ind_ls=[]
        m = np.array(re.findall(hp, rawtxt)) # original header...
        re_m = np.array([(re.sub(header_lang, '', x)).lower().strip() for x in m]) # clean header...
        mask = np.in1d(re_m, match_list)# match with clean header
        x_ind = np.where(mask == True)[0]

        if len(x_ind) > 0:
            header =re_m[mask] # clean header
        header = list(header)
    
        ind_ls = list(x_ind)

        mask = np.in1d(header, danger7)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
#            print(x_ind)
            mask = np.in1d(header[temp+1:min(temp+3, bound+1)], after_danger7)
            x_ind = np.where(mask == True)[0]
#            print(x_ind)
            if len(x_ind) > 0:
                temp2 = max(x_ind)
                if temp2 + 1 == len(x_ind):
                    header = header[:temp+1] + header[min(temp+temp2+2, bound+1): bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+temp2+2, bound+1): bound+1]


        mask = np.in1d(header, danger10)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
#            print(x_ind)
            mask = np.in1d(header[temp+1:min(temp+3, bound+1)], after_danger10)
            x_ind = np.where(mask == True)[0]
#            print(x_ind)
            if len(x_ind) > 0:
                temp2 = max(x_ind)
                if temp2 + 1 == len(x_ind):
                    header = header[:temp+1] + header[min(temp+temp2+2, bound+1): bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+temp2+2, bound+1): bound+1]
                    
                    
        mask = np.in1d(header, danger13)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger13: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check

                    
                    
        mask = np.in1d(header, danger)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
            mask = np.in1d(header[temp+1:min(temp+4, bound+1)], after_danger)
            x_ind = np.where(mask == True)[0]
            if len(x_ind) > 0:
                temp2 = max(x_ind)
                if temp2 + 1 == len(x_ind):
                    header = header[:temp+1] + header[min(temp+temp2+2, bound+1): bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+temp2+2, bound+1): bound+1]

        mask = np.in1d(header, danger4)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger4: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
#                         print(header)

        mask = np.in1d(header, danger8)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger8: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
#                         print(header)

        mask = np.in1d(header, danger11)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger11: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
                        
                        
        mask = np.in1d(header, danger14)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger14: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check

                        
        mask = np.in1d(header, danger5)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger5: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check


        mask = np.in1d(header, danger15)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            for temp in x_ind:# since orders can appear for multiple times
                bound = len(header) - 1
                if temp < bound: # check in case of out of boundry
                    if header[temp + 1] in after_danger15: 
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1] # check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
                        
                
        mask = np.in1d(header, danger2)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            bound = len(header) - 1
            for temp in x_ind:
                if temp < bound:
                    while header[temp + 1] in after_danger2:
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]# check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
                        bound = len(header) - 1
                        if temp+1 > bound:
                            break
                
        mask = np.in1d(header, danger3)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            bound = len(header) - 1
            for temp in x_ind:
                if temp < bound:
                    while header[temp + 1] in after_danger3:
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]# check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
                        bound = len(header) - 1
                        if temp+1 > bound:
                            break
            
        mask = np.in1d(header, danger12)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            x_ind[::-1].sort()
            bound = len(header) - 1
            for temp in x_ind:
                if temp < bound:
                    while header[temp + 1] in after_danger12:
                        header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]# check
                        ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1] # check
                        bound = len(header) - 1
                        if temp+1 > bound:
                            break

        mask = np.in1d(header, danger6)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
            if temp < bound:
                if header[temp + 1] in after_danger6:
                    header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1]
                
        mask = np.in1d(header, danger16)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
            if temp < bound:
                if header[temp + 1] in after_danger16:
                    header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1]
                
        mask = np.in1d(header, danger9)
        x_ind = np.where(mask == True)[0]
        if len(x_ind) > 0:
            bound = len(header) - 1
            temp = x_ind[0]
            if temp < bound:
                if header[temp + 1] in after_danger9:
                    header = header[:temp+1] + header[min(temp+2, bound+1):bound+1]
                    ind_ls = ind_ls[:temp+1] + ind_ls[min(temp+2, bound+1):bound+1]
                    

        match_hp.append(header)
        pos.append(ind_ls)
        match_len.append(len(set(header)))

    i = match_len.index(max(match_len))
    split_raw = re.split(hp_list[i], rawtxt)
    header = ['personal info'] + match_hp[i]
    match_ind = [0] +  pos[i] + [int((len(split_raw)+1)/2)]

    n = len(match_ind) - 1
    result.append(''.join(split_raw[0:(2*match_ind[1]+1)]))
    for i in range(1,n):
        tmp = ''.join(split_raw[(2*match_ind[i]+1):(2*match_ind[i+1]+1)])
        result.append(tmp)
    result[0] = re.split(pp_start, result[0])[-1]
    tmp = re.split(pp_end, result[-1])
    if len(tmp) > 3:
        result[-1] = ''.join(tmp[:3])
    else:
        result[-1] = tmp[0]
    if save_flag == 1:
        tmp = '\n==========\n'.join(result)
        with open(Path(save_folder) / (save_name + '.txt'), 'w') as f:
            f.write(tmp)

    return header, result


# medications/medication
MED = ['medications','medication','current medication', 'current medications','current meds', 
      'medication list', 'medication history', 'systemic medications','meds',
      'current outpatient prescriptions on file prior to visit','current outpatient prescriptions',
      'medication changes', 'current meds i', 'medication reviewed', 'active medications', 'prescriptions',
      'documented medications','past meds', 'medication grid', 'rome medications',
      'current medisations', 'current medisations', 'medicationlist',
      'current medications from other provider',
      'medications active prior to today','summary of medications',
      'current medications verified','current m edication',
      'medications added continued or stopped this visit']
# disease and symptoms
HPI = ['history of present illness', 'history of present lliness','history of present lilness',
      'history of present liiness', 'history of present lllness', 'history of present iliness',
       'hpifirst visit with me', 'history of present hiness', 'history of present illness',
       'hpi','history of presenting lliness','history present illness',
       'history of presenting illness','cc / hpi',
       'history of present lliness', 'clinic visit', 'chief complaint/history of present illness',
       'active problems', 'hpi comments','hpl',
      'history of present illness hpd','history ofpresent illness',
      'historyofpresent lliness', 'history ofpresentillness']
ROS = ['review of systems', 'ros','physical exam', 'examination', 'feview of systems',
       'physical findings', 'lab results', 'physical examination','pe', 'pqrs checklist',
      'fhystcal examination', 'exam','exams', 'objective findings','physical exam oo',
       'review of systems ros','examination je',
      'physicial exam','reviewofsystems',
      'review ofsystems',
      'lab result']
CC =['chief complaint','chief complaints','subjective', 'reason for appointment', 'reason for visit',
    'reason tor appointment', 'current problems','reason for visi', 'complaints', 
    'reason for visit nurse/ma', 'reason for consultation',
    'reason forvisit']
# vitals and anatomical mentions     vitals can be at physical finding/objective vital signs removed
VIT = ['vitals & measurements', 'vitals','objective','clinic vitals','visit vitals',
       'vital signs', 'vitals for this encounter']
# diagnosis and procedures
diseases = ['assessment plan', 'assessment / plan', 'plans', 'assessment and recommendations',
            'discussion and plan', 'patient active problem list','a/p','aip',
            'assessment', 'assessments','assessment/plan','assessments','diagnosis, assessment & plan',
            'assessment and plan', 'plan of care','major problem list','problem list', 'diagnosis and history',
            'assessment&plan','diagnoses', 'plan', 'assessment & plan','recommendation/plan',
           'visit diagnoses','visit diagnosis', 'other problems', 'encounter diagnosis','problems',
            'diagnosis','treatment/plan','care plan','current diagnoses','ap',
           'assessment and tx plan', 'impression and plan', 'health mgmt plan',
           'asgesbment','ansessmsnl','treatment / plan',
           'problem list/past medical history','rec/plan/discussion',
           'recommendations','all problems', 'primary diagnosis',
           'impression', 'impressions','current problems verified',
           'impression & recommendations','l surgical history',
           'diagnosis assessment & plan','problem list items addressed this visit',
           'active problem list','messe rs','assessment& plan']
# procedures under plan remove Completed Action List remove labs
procedures = ['procedures','past surgical', 'past surgical history','medical history', 
              'surgical history','past medical/surgical history','past medical',
              'past medical history','therapy','inst',
              'past medical/surgical history', 'past orders', 'past medicat history',
             'screening', 'preventive medicine', 'preventive','radiology orders', 'procedure documentation',
             'esarmination', 'orders',
             'health maintenance',
             'completed orders this encounter',
             'patient instructions',
             'process orders',
             'diagnostic services completed this visit']
# remove family
history = ['family history','family medical history', 'social history', 'secial history',
           'pregnancy/birth', 'treatment','gyn history', 'personal hx',
          'social hx', 'hospitalization/major diagnostic procedure', 'surgical / procedural history',
          'previous tests', 'medical/surgical/interim history', 'past mledical history', 'ob history', 'obstetric history',
          'tests', 'previous therapy', 'medical hx','interim history','past general medical history',
          'reproductive history', 'family histor', 'meospitalization/major diagnostic procedure',
          'pfsh','pmh/fmh/sh', 'procedure history','psh', 'family hx','pmh','sh','fh',
          'interval history', 'personal history', 'family health history', 'sociat history',
          'procedure/surgical history','proviotis tests',
          'past general surgical history','family medical history  reviewed',
          'risk factors reviewed','social history  reviewed', 'risk factors  reviewed',
          'past medical/surgical history  detailed', 'diagnostics history',
          'family history  detailed', 'social history  detailed',
          'mental health history', 'menstrual history','pregnancy history',
          'personal/social history', 'surgical history  reviewed',
          'past medical history   reviewed',
          'family history  reviewed','hospitalization/nmajor diagnostic procedure',
          'preventive care   reviewed',
           'current medications  medications reviewed',
           'current allergies   allergies/adverse reactions reviewed',
           'social histor','results / interpretations',
           'pregnancy /birth','past gyn history',
           'past medical historv','pregnancy / birth',
           'family medicalhistory','past surgicalhistory',
          ]
# exlude  'depression screening','sensory exam screening',eye exam ? advance directive
other = ['allergy','allergies','allergy list','known allergies','patient allergies','allergles',
         'active allergies/adverse reactions','allergies verified','medication allergies',
         'procedure codes','allergies/adverse reactions',
         'discussion/summary','level of service','care team',
        'health reminders','health risk assessment', 'clinical review panels',
         'counseling/education','patient coverages','vaccinations','immunizations','immunization',
        'functional assessment', 'encounter status','vaccines', 'addenda',
        'additional documentation', 'encounter report', 'immunizations given', 'patient\'s care team',
        'patient\'s pharmacies', 'other results', 'advanced care planning','documents for discussion', 
         'practice management', 'referred here', 'health care screening','results/data','lab orders',
         'transitional care','data review','lab/test results','diagnosis and procedure summary',
        'laboratory data','custom flowsheets', 'plan note',
        'review / management','patient encounters', 'referrals','directives verified',
        'review of history','results from preventive gaps',
        'risk evaluations','patient care management',
        'patient education and counseling','discussion notes',
        'counseling /education',
        'patient referrals related to this visit',
        'services performed',
        'services ordered','completed action list', 'patient information']
# if any other heder we want the code to catch, add it to above list

match_list = MED+HPI+ROS+CC+VIT+diseases+procedures+other+history

# header pattern
hp_list = []
# hp_list.append(re.compile(r'((?<=\n)[A-Z][a-zA-Z /&]{1,25}(?=\n))'))
# hp_list.append(re.compile(r'((?<=\n)[A-Z][a-zA-Z ]{1,25}(?=\:\n))'))
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][A-Z/\'& \-.,;]{1,56}(?=\s{1,5}))'))
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][A-Z/\'& \-.,;]{1,56}(?=\:*\s{1,5}))'))
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][a-zA-Z\'/& \-.,;]{1,56}(?=\:*\s{0,2}\:*\n\s{0,5}))'))
# add star after \:
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][a-zA-Z/\'& \-.,;]{1,56}(?=\:\s{1,5}))'))
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][a-zA-Z/\'& \-.,:;]{1,56}(?=\s{1,5}))'))
hp_list.append(re.compile(r'((?<=\n)[A-Zc.,:; ][a-zA-Z/\'& \-.,:;]{1,56}?(?=\s{1,5}))'))# newly added
# hp_list.append(re.compile(r'( {2,5}[A-Z ][a-zA-Z ]{1,55}(?=\:\s{2,5}))'))
pp_end = re.compile(r'(Web Link|Encounter Sign-Off|Lab Results|Sign off|PAGE|Page\s*[0-9]|[0-9]\s*of[0-9]|Provider Phone Number|electronically signed|Electronically Signed|Electronically signed|WebLink)')
pp_start = re.compile(r'(Web Link|Lab Results|PAGE|Page\s*[0-9]|Provider Phone Number|http)')
# normal language pattern
normal_lang = re.compile(r'[^\-.,/&?\':;a-zA-z0-9\s]')
# header language pattern
header_lang = re.compile(r'[^/&\'a-zA-z\s]')
# lower case initial inside upper
cap = re.compile(r'[A-Z]$')

# uncomment
# ...if ner extraction has not already happened, and we dont have extracted ner files
# also if we want to run the whole process code and log the errors

#-------------------------------------------------------------------------------------------------
#load trained models
model_anatomy = SequenceTagger.load(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Flair\BioFLAIR-master\models\anatem\best-model.pt')
model_drug_chemical = SequenceTagger.load(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Flair\BioFLAIR-master\models\bc5cdr-chem\best-model.pt')
model_procedure = SequenceTagger.load(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Flair\BioFLAIR-master\models\medm-proc-copy\best-model.pt')
model_diease_symptom = SequenceTagger.load(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Flair\BioFLAIR-master\models\ncbi\final-model.pt')
model_demo_date_loc = SequenceTagger.load('ner-ontonotes')


def get_anatomy(sent_list):
    model_anatomy.predict(sent_list)
    return sent_list


def get_drug_chemical(sent_list):
    model_drug_chemical.predict(sent_list)
    return sent_list


def get_procedure(sent_list):
    model_procedure.predict(sent_list)
    return sent_list


def get_diease_symptom(sent_list):
    model_diease_symptom.predict(sent_list)
    return sent_list

def get_demo_date(sent_list):
    model_demo_date_loc.predict(sent_list)
    return sent_list


flair_models = [get_anatomy, get_drug_chemical, get_procedure, get_diease_symptom]
#----------------------------------------------------------------------------------


model_map = {
    0: 'anatomy',
    1: 'drug&chem',
    2: 'procedure',
    3: 'disease&symptom',
    4: 'demo_date'
}


def get_ner_dict(header, result, p_flag = -1):
    """
    p_flag to print the result out, refer to model_map for more info
    """

    tagged = [[],[],[],[],[]]
    origin = []
    origin_demo = []
    ind = [0]
    for i in range(len(header)):
        tmp = split_single(result[i])
        # for first four models
        sentences = [Sentence(re.sub(r'[^a-zA-Z0-9 ]', ' ', sent.lower().replace(u'\xa0', u' '))) for sent in tmp]
        # for demo_onto model
        sentences_demo = [Sentence(re.sub(r'[^.,\'a-zA-Z0-9 ]', ' ', sent.replace(u'\xa0', u' '))) for sent in tmp]

        origin.extend(sentences)
        origin_demo.extend(sentences_demo)

        ind.append(len(sentences))
    ind = np.cumsum(ind)

    for j in range(len(flair_models)):
        for sent in flair_models[j](origin):
            tagged[j].append(sent.to_dict(tag_type = 'ner'))

    for sent in get_demo_date(origin_demo):
        all_tag = sent.to_dict(tag_type = 'ner')
        # all_tag = [item for item in all_tag if
        #            ('DAT' in str(item)) | ('PER' in str(item)) | ('GPE' in str(item)) | ('ORG' in str(item))]

        tmp = all_tag['entities'].copy()
        for en in tmp:
            if en.get('type') in ['PERSON', 'GPE', 'DATE']:
                pass
            else:
                all_tag['entities'].remove(en)

        tagged[j+1].append(all_tag)

    if p_flag in range(len(flair_models)+1):
        for i in range(len(header)):
            print(header[i]+'\n')
            for j in range(ind[i], ind[i+1]):
                print(tagged[p_flag][j])
            print('='*60)

    return ind, tagged


def save_ner_dict(header, ind, tagged, filename, save_flag = 1):
    """
    save ner dict to json file when save_flag = 1
    else return json obj with header tag
    """

    all_data = {}

    for i in range(len(flair_models)+1):
        data = {}
        tmp = tagged[i]
        for j in range(len(header)):
            data[header[j]] = tmp[ind[j]:ind[j+1]]
        all_data[model_map[i]] = data

    if save_flag == 1:
        with open(filename + '.json', 'w') as f:
            json.dump(all_data, f, indent=4)

    return all_data


def start_whole_process(filepath, config, logger, save_flag = 0):
    """
    process the file and log the error
    filepath: Path obj for input file
    save_flag: 1: get the ner json saved; 0: don't save
    return: ner json obj
    """

    pass_flag = True
    name = str(filepath.stem)
    logger.info(f'{name} start process')
    # whole_process = [readable_pdf_to_txt, split_by_header, get_ner_dict, save_ner_dict]
    #
    # for step in whole_process:
    #     if pass_flag:
    #         try:
    #             rawtxt = step(filepath)
    #         except Exception as e:
    #             pass_flag = False
    #             logging.error(f'{name} file raised an error at {step.__name__}')

    try:
        rawtxt = readable_pdf_to_txt(filepath)
    except Exception as e:
        pass_flag = False
        logger.error(f'{name} file raised an error at readable_pdf_to_txt')
        logger.error(e)

    if pass_flag:
        try:
            header, result = split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt)
        except Exception as e:
            pass_flag = False
            logger.error(f'{name} file raised an error at split_by_header')
            logger.error(e)

    if pass_flag:
        try:
            ind, tagged = get_ner_dict(header, result)
        except Exception as e:
            pass_flag = False
            logger.error(f'{name} file raised an error at get_ner_dict')
            logger.error(e)

    if pass_flag:
        try:
            all_data = save_ner_dict(header, ind, tagged, Path(config['PATH']['output'])/str(filepath.stem), save_flag)
        except Exception as e:
            pass_flag = False
            logger.error(f'{name} file raised an error at get_ner_dict')
            logger.error(e)

    if not pass_flag:
        shutil.move((str(filepath.stem)+str(filepath.suffix)), config['PATH']['error'])

    return all_data


# these two functions below are used for webapp and are not in FB whole process code..becuse they dont need web app..
def get_ner_entity(header, result, p_flag = -1):
    """
    p_flag to print the result out, refer to model_map for more info
    """

    tagged = [[], [], [], [], []]
    origin = []
    origin_demo = []
    ind = [0]
    for i in range(len(header)):
        tmp = split_single(result[i])
        # for first four models
        sentences = [Sentence(re.sub(r'[^a-zA-Z0-9 ]', ' ', sent.lower().replace(u'\xa0', u' '))) for sent in tmp]
        # for demo_onto model
        sentences_demo = [Sentence(re.sub(r'[^.,:\'a-zA-Z0-9/\ ]', ' ', sent.replace(u'\xa0', u' '))) for sent in tmp]

        origin.extend(sentences)
        origin_demo.extend(sentences_demo)

        ind.append(len(sentences))
    ind = np.cumsum(ind)

    for j in range(len(flair_models)):
        for sent in flair_models[j](origin):
            tagged[j].append(sent.get_spans('ner'))

    for sent in get_demo_date(origin_demo):
        all_tag = sent.get_spans('ner')
        # all_tag = [item for item in all_tag if
        #            ('DAT' in str(item)) | ('PER' in str(item)) | ('GPE' in str(item)) | ('ORG' in str(item))]
        all_tag = [item for item in all_tag if ('DAT' in str(item)) | ('PER' in str(item)) | ('GPE' in str(item))]
        tagged[j + 1].append(all_tag)

    if p_flag in range(len(flair_models)+1):
        for i in range(len(header)):
            print(header[i] + '\n')
            for j in range(ind[i], ind[i + 1]):
                print(tagged[p_flag][j])
            print('=' * 60)

    return ind, tagged


def get_ner_for_app(file):
    """
    get the txt files for web app ner section
    """
    rawtxt = readable_pdf_to_txt(file)
    header, result = split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt)
    ind, tagged = get_ner_entity(header, result)
    for p_flag in range(len(flair_models)+1):
        with open(str(file.stem) + '_' + str(p_flag) + '.txt', 'w') as f:            
            for i in range(len(header)):
                f.write(header[i] + '\n')
                for j in range(ind[i], ind[i+1]):
                    if len(tagged[p_flag][j]) > 0:
                        f.write(str(tagged[p_flag][j])+'\n')
                f.write('='*60+'\n')
    return 1


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('whole_process.ini')

    logging.basicConfig(filename=config['LOG']['error'], filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('readable_pdf_to_ner')
    logger.setLevel(logging.INFO)
    sample = [item for item in Path(config['PATH']['input']).iterdir() if item.suffix == '.pdf']

# uncomment below, if we want to save the extraxted text, segmented text, and ner files in respective folders
#-------------------------------------------------------------------------------------------------------------
# this is for web app ner section
    os.chdir(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Code\web_app_whole_process\web_app_whole_process\static\ner')
    #get_ner_for_app(sample[0])
    
    for i in range(len(sample)):
        get_ner_for_app(sample[i])
                        
    #[get_ner_for_app(sample[i]) for i in range(len(sample))]
    
# if the input folder has more than one sample file, loop over the files with get_ner_for_app(sample[i])

# this is for save test
#     rawtxt = readable_pdf_to_txt(sample[0], save_flag=1, save_folder=r'\Users\Sri\Google Drive\Icube\FloridaBlue\Code\web_app_whole_process\web_app_whole_process\static\text')
#     header, result = split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt, save_name=str(sample[0].stem)+'_seg', save_flag=1, save_folder=r'\Users\Sri\Google Drive\Icube\FloridaBlue\Code\web_app_whole_process\web_app_whole_process\static\segmented')
#--------------------------------------------------------------------------------------------------------------------

# if we want to run the whole process code, and log the errors comment above, and uncomment below
#------------------------------------------------
# this is whole process for FB
# can start loop over sample here
# if we want to save the json file, as described above in the start_whole_process function, put save_flag = 1, in the below arguments.

    #all_data = start_whole_process(sample[0], config, logger)
    #all_data = start_whole_process(sample[0], config, logger, save_flag = 1)
# end loop

    print('done')



    # config = configparser.ConfigParser()
    # config['PATH'] = {
    #     'input': r'/Users/xuqinxin/PycharmProjects/web_app_whole_process/static/readable_sample',
    #     'output': r'/Users/xuqinxin/PycharmProjects/web_app_whole_process/good_eg',
    #     'error': r'/Users/xuqinxin/PycharmProjects/web_app_whole_process/error_eg'
    # }
    # config['LOG'] = {
    #     'error': r'/Users/xuqinxin/PycharmProjects/web_app_whole_process/whole_process.log'
    # }
    # with open('whole_process.ini', 'w') as configfile:
    #     config.write(configfile)