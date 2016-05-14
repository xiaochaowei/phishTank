# import cv2
# import numpy as np
# #read img 
# img1 = cv2.imread('test/1.jpg')
# img2 = cv2.imread('test/2.jpg')
# gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
# detector = cv2.SIFT()
import MySQLdb
conn = MySQLdb.connect(user = 'root', passwd = '19920930', db = 'PhishTank')
cursor = conn.cursor()

QUERY_URL = " SELECT phish_id, url FROM phishTank2;"
cursor.execute(QUERY_URL)
rows = cursor.fetchall()
url_list = []
UPDATE_IP = """ UPDATE phishTank2 SET ips = "{ips}", sub_time = "{sub_time}" where phish_id = {phish_id} """
QUERY_IP = """ SELECT ips, sub_time from solved where url = "{url}" ; """

for row in rows:
	url = row[1]
	phish_id = row[0]
	comment_sql = QUERY_IP.format(url = url)
	cursor.execute(comment_sql)
	rows = cursor.fetchall()
	if len(rows) > 0:
		ips = rows[0][0]
		sub_time = row[0][1]
		comment_sql = UPDATE.format(ips = ips, sub_time = sub_time, phish_id = phish_id)
		cursor.execute(comment_sql)
		conn.commit()
