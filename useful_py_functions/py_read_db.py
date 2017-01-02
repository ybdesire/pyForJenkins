try:
	conn=pymysql.connect(host='10.1.1.1', user='username', passwd='passwd', db='data_base', port=3306)
	cur=conn.cursor()

	cur.execute('select * from {0} WHERE sha256=0x{1}'.format(db_table, sha256))  
	data=cur.fetchall()
	if(data!=()):
		return [data[0][0], data[0][1]]
	else:
		return ['', '']
	cur.close()
	conn.close() 
except Exception as e:
	print('exception: {}'.format(e))