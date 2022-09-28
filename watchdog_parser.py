#/usr/bin/python3
'''
Created on 2022/09/27

@author: ZL Chen
@title: Watchdog Status Parser
'''

from subprocess import check_output
from pymysql import connect
from time import *
import re

class watchdog(object):
	'''
	Timezone: UTC+8 to UTC
	'''
	def datetime_taiwan_to_utc(self, datetime):
		taiwan_time = strptime(datetime, "%Y-%m-%d %H:%M:%S")
		taiwan_time = mktime(taiwan_time)
		utc_time = taiwan_time - 8 * 60 * 60
		utc_time = localtime(utc_time)
		new_time = strftime('%Y-%m-%d %H:%M:%S', utc_time)
		return new_time
		
	'''
	Watchdog information parser: Watchdog status parser
	'''
	def _watchdog_parser(self):
		die_status = bool()
		cu_tail = 'tail -n 30 /mnt/log/watchdog.log'
		# cu_tail = 'tail -n 15 20220923_07_watchdog.log'
		re_cu = check_output(cu_tail, shell=True).decode('utf-8').strip()

		# contentRex
		find_cu_str = r'Watchdog kicks missed=\d+.*\D(.*) cmd ok:(\D+)\d+.*Watchdog collect die log complete.'
		contentRex = re.findall(find_cu_str, re_cu)
		# print(contentRex)
		re_contentRex = ' '.join(contentRex[0])
		re_contentRex = re_contentRex.split(' ')
		# print(re_contentRex)
		timerRex = re_contentRex[0] + ' ' + re_contentRex[1]
		# print(timerRex)
		utc_time = self.datetime_taiwan_to_utc(timerRex)
		print(utc_time)
		ip = self._ip_parser()
		print(ip)

		# DIE check
		die_check = re_contentRex[2] + ' ' + re_contentRex[3]
		if die_check == '[logCollect die]\n':
			print('value')
			die_status = True
			self.insert_database(utc_time, ip, die_status)
		else:
			print('no value')
			die_status = False
			self.insert_database(utc_time, ip, die_status)
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
	def insert_database(self, datetime, ip, die_status):
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
			sql = """INSERT INTO {table}(DateTime , IP, DIE_CHECK) \
				VALUES(%s, %s, %s)""".format(table='watchdog')
			# print(sql)
			cur.execute(sql, (datetime, ip, die_status))
			conn.commit()
			print('The information is commit to database.')
		except Exception as e:
			# raise e
			pass

if __name__ == '__main__':
	while True:
		func = watchdog()
		func._watchdog_parser()
		sleep(3)