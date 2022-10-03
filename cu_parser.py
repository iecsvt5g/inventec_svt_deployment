#/usr/bin/python3
'''
Created on 2022/09/27

@author: ZL Chen
@title: CU Parser
'''

from subprocess import check_output
from pymysql import connect
from time import *
import re

class cu(object):
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
	CU information parser: DateTime, IP, DL_PDCP_Ingress, DL_PDCP_Egress, UL_PDCP_Ingress, UL_PDCP_Egress
	DL_GTPU_Ingress, DL_GTPU_Egress
	'''
	def _cu_parser(self):
		while True:
			cu_tail = 'tail -n 100 /home/BaiBBU_XSS/BaiBBU_SXSS/CU/bin/pdcp.log'
			# cu_tail = 'tail -n 100 20220927_16_pdcp.log'
			re_cu = check_output(cu_tail, shell=True).decode('utf-8').strip()
			# contentRex
			find_cu_str = r'DL GTPU ingress traffic\D+(\d+.\d+) bps\D+(\d+.\d+)\D+Timer:(\D+\d+\D+\d+\D+\d+\D+\d+\D+\d+)\D+DL PDCP ingress traffic\D+(\d+.\d+) bps\D+egress traffic\D+(\d+.\d+) bps .*\D+UL PDCP ingress traffic\D+(\d+.\d+) bps\D+egress traffic\D+(\d+.\d+) bps .*\D+.*\D+.*\D'
			contentRex = re.findall(find_cu_str, re_cu)
			if len(contentRex) == 0:
				break
			else:
				contentRex = contentRex[:]
				# print(contentRex)
				len_contentRex = len(contentRex)-1
				re_contentRex = contentRex[len_contentRex]
				# print(re_contentRex)
				timerRex = re_contentRex[2]
				# print(timerRex)
				utc_time = self.datetime_taiwan_to_utc(timerRex)
				print(utc_time)
				ip = self._ip_parser()
				print(ip)
				print('DL GTPU ingress traffic', re_contentRex[0])
				print('DL GTPU egress traffic', re_contentRex[1])
				print('DL PDCP ingress traffic', re_contentRex[3])
				print('DL PDCP egress traffic', re_contentRex[4])
				print('UL PDCP ingress traffic', re_contentRex[5])
				print('UL PDCP egress traffic', re_contentRex[6])
				self.insert_database(utc_time, ip, re_contentRex[5], re_contentRex[6], re_contentRex[3], re_contentRex[4], re_contentRex[0], re_contentRex[1])
				break

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
	def insert_database(self, datetime, ip, dl_pdcp_ingress, dl_pdcp_egress, ul_pdcp_ingress, ul_pdcp_egress, dl_gtpu_ingress, dl_gtpu_egress):
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
			sql = """INSERT INTO {table}(DateTime , IP, DL_PDCP_Ingress, DL_PDCP_Egress, UL_PDCP_Ingress, UL_PDCP_Egress, DL_GTPU_Ingress, DL_GTPU_Egress) \
				VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""".format(table='cu')
			# print(sql)
			cur.execute(sql, (datetime, ip, dl_pdcp_ingress, dl_pdcp_egress, ul_pdcp_ingress, ul_pdcp_egress, dl_gtpu_ingress, dl_gtpu_egress))
			conn.commit()
			print('The information is commit to database.')
		except Exception as e:
			# raise e
			pass

if __name__ == '__main__':
	while True:
		func = cu()
		func._cu_parser()
		sleep(3)