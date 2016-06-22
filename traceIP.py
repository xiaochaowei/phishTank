from bs4 import BeautifulSoup
import urllib2
import gzip
from StringIO import StringIO
import MySQLdb
PREFIX = "http://www.securityspace.com/sprobe/doprobe.html?URL="
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = "phishTank")
cursor = conn.cursor()
def ungzip(data):		
	buf = StringIO(data)		
	f = gzip.GzipFile(fileobj = buf)
	source = f.read()
	return source

def urlcrawl(url):
	str_list = []
	try:
		abs_url = PREFIX + url
		print abs_url
		req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',\
					'Accept':'text/html;q=0.9,*/*;q=0.8',\
					'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',\
					'Accept-Encoding':'gzip',\
					'Connection':'close',\
					'Referer':None }
		req_timeout = 20
		req = urllib2.Request(abs_url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			source = ungzip(resp.read())
		else:
			source = resp.read()
		fid = open('test.html', 'w')
		fid.write(source)
		fid.close()
		return source
		# if 0:
		soup = BeautifulSoup(source)
		trs = soup.body.find_all("tr", class_ = "small")
		if not len(trs) == 0:
			for i in range(0, len(trs)):
				item = trs[i]
				tds = item.find_all('td')
				date = tds[1].get_text()
				ip = tds[3].get_text()
				server_str = tds[5].get_text()
				tmp = date + "," + ip + "," + server_str
				str_list.append(tmp)
		return str_list
	except Exception as e:
		print e
		return str_list
	# item = table.find_all('tr')
	# for i in range(2, 3):
	# 	ins = item[i].find_all('td')
	# 	print ins

INSERT_SQL = """ INSERT INTO traceip(date, ip, server, phish_id) VALUES ("{date}", "{ip}", "{server}", {phish_id}) ;""" 
QUERY_SQL = """SELECT distinct(url), phish_id FROM phishTank2 WHERE valid like "%VALID PHISH%" and online like "%ONLINE%"; """ 
comment_sql = QUERY_SQL
cursor.execute(comment_sql)
rows = cursor.fetchall()
for row in rows:
	phish_id = row[1]
	url = row[0]
	str_list = urlcrawl(url)
	if len(str_list):
		continue
	else:
		for tmp_str in str_list:
			tmp = tmp_str.split(",")
			comment_sql = INSERT_SQL.format(date = tmp[0], ip = tmp[1], server = tmp[2], phish_id = phish_id)
			cursor.execute(comment_sql)
		conn.commit()
