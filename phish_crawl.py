from bs4 import BeautifulSoup
import urllib2
import MySQLdb
import gzip
from StringIO import StringIO
import sys
import datetime
import time
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = "PhishTank")
cursor = conn.cursor()
# SELECTSQL = """ SELECT phish_id, DATE_FORMAT(submission_time ,"%Y-%m-%d") FROM phishTank WHERE phish_id = "{phish_id}" ; """
UPDATESQL = """ UPDATE phishTank2  SET url = "{url}", submission_time = "{submission_time}", valid = "{valid}" , online = "{online}", flag = {flag} WHERE phish_id = {phish_id}; """
QUERYSQL =  """ SELECT 	phish_id, url, submission_time, valid, online FROM phishTank2 where phish_id = {phish_id}; """ 
INSERTSQL = """ INSERT INTO phishTank2(phish_id, url, submission_time, valid, online) values ({phish_id}, "{url}", "{submission_time}", "{valid}", "{online}"); """ 
def extractDate(date_str):
	tmp = date_str.split(" ")
	date_format = """{month} {day} {year} {time} {eq}"""
	time_str = date_format.format(month = tmp[2], day = tmp[3][:-2], year = tmp[4], time = tmp[5], eq = tmp[6])
	return datetime.datetime.strptime(time_str, "%b %d %Y %I:%M %p").strftime("%Y-%m-%d %I:%M %p")

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
			soup = BeautifulSoup(source)
			table = soup.table
			item = table.find_all('tr')
			for i in range(1,len(item)):
				
				flag = 0
				try:
					ins = item[i].find_all('td')
					phish_id = ins[0].a.contents[0]
				#	print phish_id
					submission_time = extractDate(ins[1].span.contents[0])
				#	print submission_time
					if datetime.datetime.strptime(submission_time, "%Y-%m-%d %I:%M %p").year == "2012":
						end_data = 1
						break
					page_url = ins[1].get_text().split(" ")[0][:-5].encode('utf-8')
					page_url = page_url[page_url.find("//")+2:]
					page_url = page_url[:page_url.find("/")]
					valid = ins[3].get_text()
					online = ins[4].get_text()
				except Exception as  e:
					print e
					continue
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
						if submission_time != row[2].split("|")[-1]:
							flag = 1
							print "PhishID: ", phish_id
						submission_time = row[2] + "|" + submission_time
						page_url = row[1] + "|" + page_url
						comment_sql = UPDATESQL.format(submission_time = submission_time,\
							url = page_url,\
							valid = valid,\
							online = online,\
							phish_id = phish_id,\
							flag = flag)
						savePicture(str(phish_id)+"_"+str(len(row[3].split("|") ) ), img_url)
						cursor.execute(comment_sql)
						conn.commit()
				else:
					comment_sql = INSERTSQL.format(phish_id = phish_id, \
						submission_time = submission_time,\
						url = page_url,\
						valid = valid,\
						online = online)
					savePicture(str(phish_id), img_url)
					cursor.execute(comment_sql)
					conn.commit()
			if soup.table.find_all('a')[-1].contents != [u'Older >'] or end_data == 1:
				print "new Loop"
				time.sleep(60* 60)
				next_page = "?page=0&valid=y&Search=Search"
			else:
				next_page = soup.table.find_all('a')[-1]['href']

			#sys.stdout.write(next_page)
			url = url_prefix + next_page
			print url
	#		return urlcrawl(url_prefix, next_page)
		except urllib2.HTTPError as e:
			print e
			time.sleep(10*60)
			# return 		
		except urllib2.URLError as e:
			print e
			time.sleep(10*60)
			# return 
		except Exception as e:
			print e
			return False


url = "https://www.phishtank.com/phish_search.php"
surffix = "?page=1&valid=y&Search=Search"
urlcrawl(url, surffix)

