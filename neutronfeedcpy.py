import Neutron as d
import nltk
import string
import pickle
import os
import time
import sys
import paramiko
import pandas as pd
import hashlib
import csv
import requests

from os import path
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

home_path ='/seclog/'
opfile_path = home_path + 'output_neutron.txt'
neulog = ['dhcp-agent.log','metering-agent.log','server.log','l3-agent.log','openvswitch-agent.log','metadata-agent.log','ovs-cleanup.log']

with open (opfile_path, 'w+') as gen:
	gen.write('start')

string.cap='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
string.spl='~!@#$%^&*()_+-=\|]}[{:;<>,./?'
string.num='0123456789'
ck_size = 512 * 1024 * 1024
hashflag = 0
line_no1 = 1
line_no2 = 0

colnames1=['uname','host']
colnames2=['hash_value','pos']
df1 = pd.read_csv('/seclog/data.csv',names=colnames1)
df2 = pd.read_csv('/seclog/hashandpos.csv',names=colnames2)
hashl = df2.hash_value.tolist()
posl = df2.pos.tolist()
unamel = df1.uname.tolist()
hostl = df1.host.tolist()
fin1 = open(home_path + 'test.csv','r+')

for i in range(1,len(hostl)):
    fh = []
    file1 = []
    file2 = []
    host=str(hostl[i])
    uname=str(unamel[i])
    line_no1 = 8       
    
    for logfile in neulog:
        s= requests.Session()
        link = 'https://192.168.0.200:8080/neutron'
        r = s.get(link,host,logfile)
        g = r.text
        fh = open('/seclog/inter.txt','w+')
        fh.seek(0)
        fh.write(g)
        if (hashl[line_no1] == '0' and posl[line_no1] == '0'):
            postemp=posl[line_no1]
            m1 = hashlib.md5()
            fh.seek(0)
            while True:
                buf = fh.read(ck_size)                  
                if not buf:
                    break
                buf = str(buf)
                m1.update(buf.encode('utf-8'))
            new_md5_sum = m1.hexdigest()
            hashl[line_no1] = (new_md5_sum)
            posl[line_no1] = int(fh.tell())
            line_no1+=1
            fh.seek(int(postemp))

        else:
            old_pos = posl[line_no1]
            old_md5_sum = hashl[line_no1]    
            m2 = hashlib.md5()
            fh.seek(0)
            while True:
                buf = fh.read(ck_size)
                if not buf:
                    break
                buf = str(buf)
                m2.update(buf.encode('utf-8'))
            new_md5_sum = m2.hexdigest()
            new_pos = fh.tell()
            
            m3 = hashlib.md5()
            fh.seek(0)
            if old_pos < ck_size:     
                buf = fh.read(old_pos)
                buf = str(buf)
                m3.update(buf.encode('utf-8'))
            else:
                while (old_pos-fh.tell()) >= ck_size:
                    buf = fh.read(ck_size)
                    buf = str(buf)
                    m3.update(buf.encode('utf-8'))
                buf = fh.read(old_pos-fh.tell())
                buf = str(buf)
                m3.update(buf.encode('utf-8'))
            check_md5_sum = m3.hexdigest()
                        
            if old_md5_sum == str(check_md5_sum):
                hashl[line_no1] = str(new_md5_sum)
                posl[line_no1] = str(new_pos)
                line_no1+=1
                fh.seek(int(old_pos))
            else:	
                fh.seek(int(old_pos))		
                hashflag = 1
                line_no1+=1        

        output = open(home_path + 'neu_check.txt','w+')

        if hashflag == 0:
            output.write('hash verified')
            tokens1 = []
            tokens = []
            tokensv = []
            tokensn = []
            temp = []
            final= []
        
            for line in fh:
                tokenst = line.split()
                tokens1.extend(tokenst)
            tokens = list(FreqDist(tokens1))
            
            fh.truncate()
            
            for word in tokens:
                if word not in d.tokens:
                    tokensv.append(word)
                else:
                    continue
            for words in tokensv:
                tokensn.append(d.generate_ngrams(words,3,1))
            i=0
            dout = []
            for word in tokensn:
                dout = d.detect_mod(word)
                if dout[0] == 'pos':
                    temp.append(tokensv[i])
                    i=i+1
                else:
                    continue
            for word in temp:
                a=0
                b=0 
                c=0 
                for i in range(len(word)):
                    if word[i] in string.cap:
                        a=1
                    if word[i] in string.num:
                        b=1
                    if word[i] in string.spl:
                        c=1
                if a==1 and b==1 and c==1:
                    final.append(word)
            with open (opfile_path, 'a+') as gen:
                gen.write('\nIn '+uname+'@'+host+' neutron '+logfile+' :\n')
                if not final:
	                gen.write('No credentials detected')
                else:
                    gen.write('\n'.join(str(word) for word in final))

        else:
            output.write('Hash verification failed')
        output.close()

wr = csv.writer(fin1)
wr.writerows(zip(hashl,posl))

with open (opfile_path, 'a+') as gen:
    gen.write('\nend')

fin1.close()


