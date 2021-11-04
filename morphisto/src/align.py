#!/usr/bin/python
# -*- coding: utf-8 -*-
import re,sys

epsilon=re.compile("0")
replacement=re.compile("[@A-Za-zäöüßÄÖÜ0éè\.]+:[@A-Za-zäöüßÄÖÜ0éè\.]+")

def align(w1,w2):
	w1_len=len(w1)
	w2_len=len(w2)
	max_len=w1_len
	if w2_len>max_len: max_len=w2_len
	while 1:
		if w1_len==max_len: break
		w1=w1+"0"
		w1_len=w1_len+1
	while 1:
		if w2_len==max_len: break
		w2=w2+"0"
		w2_len=w2_len+1
	result=""
	for i in range(0,max_len):
		if w1[i]==w2[i]: 
			result+=w1[i]
			continue
		if w1[i]!=w2[i]:
			result+=w1[i]+":"+w2[i]
	result=epsilon.sub("<>",result)
	return result

#print align("Maus".decode('utf-8'),"Mäus".decode('utf-8'))
data=sys.stdin.readlines()
for line in data:
	try:
		foo=replacement.search(line).group()
		bar=foo.split(":")
		dummy=align(bar[0].decode('utf-8'),bar[1].decode('utf-8'))
		doof=re.sub(foo,dummy,line,re.UNICODE)
		sys.stdout.write(doof.encode('utf-8'))
	except:
		sys.stdout.write(line)

