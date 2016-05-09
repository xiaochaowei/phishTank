from bs4 import BeautifulSoup
import urllib2
import MySQLdb
import gzip
from StringIO import StringIO
import sys
import datetime
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = "PhishTank")
cursor = conn.cursor()
# SELECTSQL = """ SELECT phish_id, DATE_FORMAT(submission_time ,"%Y-%m-%d") FROM phishTank WHERE phish_id = "{phish_id}" ; """
UPDATESQL = """ UPDATE phishTank  SET url = "{url}", submission_time = "{submission_time}", valid = "{valid}" , online = "{online}" WHERE phish_id = {phish_id}; """
QUERYSQL =  """ SELECT 	phish_id, url, submission_time, valid, online FROM phishTank where phish_id = {phish_id}; """ 
INSERTSQL = """ INSERT INTO phishTank(phish_id, url, submission_time, valid, online) values ({phish_id}, "{url}", "{submission_time}", "{valid}", "{online}"); """ 
def extractDate(date_str):
	tmp = date_str.split(" ")
	date_format = """{month} {day} {year}"""
	return datetime.datetime.strptime(date_format.format(month = tmp[2], day = tmp[3][:-2], year = tmp[4]), "%b %d %Y").strftime("%Y-%m-%d")

def ungzip(data):		
	buf = StringIO(data)		
	f = gzip.GzipFile(fileobj = buf)
	source = f.read()
	return source

def savePicture(filename, url):
	try:
		req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',\
			'Accept':'text/html;q=0.9,*/*;q=0.8',\
			'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',\
			'Accept-Encoding':'gzip',\
			'Connection':'close',\
			'Referer':None }
		req_timeout = 10
		req = urllib2.Request(url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			source = ungzip(resp.read())
		else:
			source = resp.read()
		soup = BeautifulSoup(source,'html.parser')
		iframe = soup.find('iframe')
		suffix = iframe['src']
		image_url = "http://www.phishtank.com/" + suffix
		print image_url
		req = urllib2.Request(image_url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			source = ungzip(resp.read())
		else:
			source = resp.read()
		soup = BeautifulSoup(source,'html.parser')
		img_src = soup.img['src']
		data = urllib2.urlopen(img_src).read()
		fid = open("img/" + filename + ".jpg",'wb')
		fid.write(data)
		fid.close()
		print "success save"
		# sys.stdout.write("save success!\n")
	except Exception as e:
		print e


def urlcrawl(url_prefix, url_surffix):
	url = url_prefix + url_surffix
	while(1):
		try:
			end_data = 0
			req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',\
				'Accept':'text/html;q=0.9,*/*;q=0.8',\
				'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',\
				'Accept-Encoding':'gzip',\
				'Connection':'close',\
				'Referer':None }
			req_timeout = 5
			req = urllib2.Request(url, None, req_header)
			resp = urllib2.urlopen(req, None, req_timeout)
			if resp.headers.get('content-encoding') == "gzip":
				source = ungzip(resp.read())
			else:
				source = resp.read()
			soup = BeautifulSoup(source,'html.parser')
			table = soup.table
			item = table.find_all('tr')
			for i in range(1,len(item)):
				ins = item[i].find_all('td')
				phish_id = ins[0].a.contents[0]
				submission_time = extractDate(ins[1].span.contents[0])
				print submission_time
				if datetime.datetime.strptime(submission_time, "%Y-%m-%d").year == "2012":
					end_data = 1
					break
				page_url = ins[1].get_text().split(" ")[0][:-5].encode('utf-8')
				valid = ins[3].get_text()
				online = ins[4].get_text()
				img_url = "https://www.phishtank.com/phish_detail.php?phish_id=" + str(phish_id)
				comment_sql = QUERYSQL.format(phish_id = phish_id)
				cursor.execute(comment_sql)
				rows = cursor.fetchall()
				if len(rows) > 0:
					assert(len(rows) == 1)
					row = rows[0]
					if row[3].split("|")[-1] != valid or row[4].split("|")[-1] != online or row[1].split("|")[-1] != page_url:
						valid = row[3] + "|" + valid
						online = row[4] + "|" + online
						submission_time = row[2] + "|" + submission_time
						page_url = row[1] + "|" + page_url
						print page_url
						print online
						print valid
						print submission_time
						comment_sql = UPDATESQL.format(submission_time = submission_time,\
							url = page_url,\
							valid = valid,\
							online = online,\
							phish_id = phish_id)
						#savePicture(str(phish_id)+"_"+str(len(row[3].split("|") ) ), img_url)
						cursor.execute(comment_sql)
						conn.commit()
				else:
					print phish_id
					comment_sql = INSERTSQL.format(phish_id = phish_id, \
						submission_time = submission_time,\
						url = page_url,\
						valid = valid,\
						online = online)
					#savePicture(str(phish_id), img_url)
					cursor.execute(comment_sql)
					conn.commit()
			if soup.table.find_all('a')[-1].contents != [u'Older >'] or end_data == 1:
				time.sleep(60* 60)
				next_page = "?page=0"
				print "new loop"
			else:
				next_page = soup.table.find_all('a')[-1]['href']
			#sys.stdout.write(next_page)
			url = url_prefix + next_page
			print next_page
	#		return urlcrawl(url_prefix, next_page)
		except urllib2.HTTPError as e:
			print e
			time.sleep(10*60)
			# return 		
		except urllib2.URLError as e:
			print e
			time.sleep(10*60)
			# return 
	#	except Exception as e:
	#		print e
			#sys.stdout.write(sys.exc_info()
			# return 
		# 	return False


url = "https://www.phishtank.com/phish_archive.php"
surffix = "?page=9949"
urlcrawl(url, surffix)

