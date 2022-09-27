#/usr/bin/python3
'''
Created on 2022/09/27

@author: ZL Chen
@title: CU Parser UE
'''

from subprocess import check_output
from pymysql import connect
from time import *
import re

class cu_ue(object):
	'''
	Timezone: UTC+8 to UTC
	'''
	def datetime_taiwan_to_utc(self, datetime):
		taiwan_time = strptime(datetime, "%a %b %d %H:%M:%S %Y")
		taiwan_time = mktime(taiwan_time)
		utc_time = taiwan_time - 8 * 60 * 60
		utc_time = localtime(utc_time)
		new_time = strftime('%Y-%m-%d %H:%M:%S', utc_time)
		return new_time
		
	'''
	CU information parser: Num_Of_Active_UE
	'''
	def _cu_parser(self):
		cu_tail = 'tail -n 15 /home/BaiBBU_XSS/BaiBBU_SXSS/CU/bin/pdcp.log'
		# cu_tail = 'tail -n 15 20220927_16_pdcp.log'
		re_cu = check_output(cu_tail, shell=True).decode('utf-8').strip()

		# contentRex
		find_cu_str = r'Timer:(\D{3}) (\D{3}) (\d{2}) (.*) (\d{4})'
		contentRex = re.findall(find_cu_str, re_cu)
		re_contentRex = ' '.join(contentRex[0])
		re_contentRex = re_contentRex.split(' ')
		timerRex = re_contentRex[0] + ' ' + re_contentRex[1] + ' ' + re_contentRex[2] + ' ' + re_contentRex[3] + ' ' + re_contentRex[4]
		# print(timerRex)
		utc_time = self.datetime_taiwan_to_utc(timerRex)
		print(utc_time)
		ip = self._ip_parser()
		print(ip)

		# number of active ue
		num_of_active_ue = r'numOfActiveUe\D{1}(\d{1})\D{1}'
		contentRex = re.findall(num_of_active_ue, re_cu)
		# print(contentRex)
		if contentRex:
			print('value')
			re_contentRex = ' '.join(contentRex[0])
			re_contentRex = int(re_contentRex)
			# print(re_contentRex, type(re_contentRex))
			self.insert_database(utc_time, ip, re_contentRex)
		else:
			print('no value')
			pass

	'''
	IP Address Parser
	'''
	def _ip_parser(self):
		try:
			ip_command = 'ip addr | grep \'inet 172.32\' | awk \'END{print $2}\''
			ip_command = check_output(ip_command, shell=True).decode("utf-8").strip()
			ip_command = ip_command.replace('/24', '')	# replace subnet mask str
			ip_command = ip_command.replace('/16', '')	# replace subnet mask str
			return ip_command
		except:
			return 'Not Found IP'

	'''
	Insert into date to MySQL (phpmyadmin)
	'''
	def insert_database(self, datetime, ip, num_of_active_ue):
		try:
			mysql_info = {
				'host': '172.32.3.153',
				'port': 3306,
				'user': 'svt',
				'password': '1qaz@WSXiecsvt5g',
				'db': 'svt'
			}
			conn = connect(**mysql_info)
			cur = conn.cursor()
			sql = """INSERT INTO {table}(DateTime , IP, Num_Of_Active_UE) \
				VALUES(%s, %s, %s)""".format(table='cu_active_ue')
			# print(sql)
			cur.execute(sql, (datetime, ip, num_of_active_ue))
			conn.commit()
			print('The information is commit to database.')
		except Exception as e:
			# raise e
			pass

if __name__ == '__main__':
	while True:
		func = cu_ue()
		func._cu_parser()
		sleep(3)