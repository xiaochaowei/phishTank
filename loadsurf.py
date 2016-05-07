import MySQLdb
conn = MySQLdb.connect(user = 'root', passwd = '19920930', db = 'PhishSurbl')
cursor = conn.cursor()
INSERT_SQL = """ INSERT INTO SURLB(url, ips, sub_time) VALUES ("{url}","{ips}", "{sub_time}") ;"""
QUERY_SQL = """ SELECT url, ips, sub_time from SURLB WHERE url = "{url}" ;""" 
UPDATE_SQL = """ UPDATE SURLB SET ips = "{ips}", sub_time = "{sub_time}" WHERE url = "{url}"; """

import os
rootDir = '/raid/reputation/merit/raw/'
file_list = os.listdir(rootDir)
for i in file_list:
	if i == "." or i == "..":
		continue
	sub_time = i
	full_name = rootDir + i + "/multi.surbl.org.resolved"
	print full_name 
	fid = open(full_name, 'r')
	data = fid.read()
	fid.close()
	data = data.split("\n")
	for idx in range(1,len(data)):
		tmp = data[idx].split("|") 
		url = tmp[0]
		ip = tmp[1]
		if ip == "NXDOMAIN":
			continue
		comment_sql = QUERY_SQL.format(url = url)
		cursor.execute(comment_sql)
		rows = cursor.fetchall()
		if len(rows) > 0:
			assert len(rows) == 1
			ip_list = rows[0][1].split('|')
			sub_time_list = rows[0][2].split('|')
			if ip in ip_list:
				print ip,'in the list '
				continue
			ip_list.append(ip)
			print ip_list
			sub_time_list.append(sub_time)
			comment_sql = UPDATE_SQL.format(ips = "|".join(ip_list), sub_time = "|".join(sub_time_list), url = url)
			cursor.execute(comment_sql)
		else:
			comment_sql = INSERT_SQL.format(url = url, ips = ip, sub_time = sub_time)
			cursor.execute(comment_sql)
	conn.commit()

