#!/usr/bin/python
# encoding=utf-8

import socket;
import re;
import urllib2;
import ssl;

user="USER titlebot titlebot irc.freenode.net :Brisk's titlebot\n";
nick="NICK titlebot_\n";
channel=['#debian_cn'];

def join_channel(ssl):
	for c in channel:
		ssl.send("JOIN "+c+"\n");

def get_channel(str):
	p=re.compile('.*(#.[^ ]*)').findall(str);
	if p:
		return p[0];
	else:
		p=re.compile(':(.[^!]*)').findall(str);
		return p[0];

def _decode(str):
	try:
		str.decode('utf-8');
		return str;
	except:
		pass;
	try:
		str.decode('gbk');
		return str.decode('gbk').encode('utf-8');
	except:
		pass;
	return str;

def pong_serv(ssl,str):
	l=list(str);
	l[1]='O';
	ssl.send(''.join(l));

def get_title(ssl,p,chan):
	for url in p:
		try:
			get=urllib2.urlopen(url).read();
		except Exception,err:
			ssl.send("PRIVMSG "+chan+" :"+str(err)+"\n");
			continue;
		temp=re.compile('<title>(.[^<]*)').findall(get);
		if temp:
			ssl.send("PRIVMSG "+chan+" :"+"标题："+_decode(temp[0])+"\n");
		else:
			ssl.send("PRIVMSG "+chan+" :啊哦，淫家木有发现标题了啦@.@\n");

def get_magnet(ssl,p,chan):
	for magnet in p:
		s1=urllib2.unquote(magnet).replace("\n"," ");
		s2=s1.replace("\r"," ");
		ssl.send("PRIVMSG "+chan+" :"+"标题："+s2+"\n");

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("irc.freenode.net",7000));
ssl=ssl.wrap_socket(s);

ssl.send(user);
ssl.send(nick);
join_channel(ssl);

while True:
    data=ssl.recv(1024);
    if not data:
	    quit();
    if 'http' and 'PRIVMSG' in data:
        p=re.compile('(http.?://[\S]*)').findall(data);
        if p:
		get_title(ssl,p,get_channel(data));
		del(p);
    p=re.compile('magnet:\?xt=urn:btih:.[^&]*&amp;dn=(.[\S]*)').findall(data);
    if p:
	    get_magnet(ssl,p,get_channel(data));
	    del(p);
    if 'PING' in data and 'PRIVMSG' not in data:
	    pong_serv(ssl,data);
    del(data);

