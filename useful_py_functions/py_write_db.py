now = datetime.datetime.now()

try:
	conn=pymysql.connect(host='10.1.1.1', user='username', passwd='passwd', db='data_base', port=3306, autocommit=True)

	cur=conn.cursor()
	
	cur.execute('INSERT INTO table2 (build_binary, nameid, threshold, submitTime) VALUES (%s, %s, 60, %s)', (bin, sid, now) )  

	cur.close()
	conn.close() 
except Exception as e:
	print('exception: {}'.format(e))