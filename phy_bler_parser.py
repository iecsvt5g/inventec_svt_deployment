#/usr/bin/python3
'''
Created on 2022/09/01

@author: ZL Chen
@title: PHY BLER Parser
'''

# import sys
# sys.path.insert(0, '../lib')
import subprocess
import pymysql
import time
# from influx_db import infulx_db
from time import sleep
from subprocess import check_output

class bler_parser(object):
	def parser(self):
		while True:
			parser_cli_0 = 'grep \"0 (Kbps)\" /home/BaiBBU_XSS/BaiBBU_PXSS/PHY/bin/Phy.log | awk \'END{print $(NF-4)}\' | sed \'s/.$//\''
			# parser_cli_1 = 'grep \"1 (Kbps)\" /home/BaiBBU_XSS/BaiBBU_PXSS/PHY/bin/Phy.log | awk \'END{print $(NF-4)}\' | sed \'s/.$//\''
			parser_response_0 = str(subprocess.check_output(parser_cli_0, shell=True)).split('b\'')[1]
			# parser_response_1 = str(subprocess.check_output(parser_cli_1, shell=True)).split('b\'')[1]
			if parser_response_0[0].isdigit():
				parser_response_0 = float(parser_response_0[0:-3])
				# parser_response_1 = float(parser_response_1[0:-3])
				print(parser_response_0)
				# print(parser_response_0, parser_response_1)
				break
			else:
				time.sleep(1)
				pass
		return parser_response_0
		# return parser_response_0, parser_response_1

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

	def cloud_db(self, _time, r_0):
	# def cloud_db(self, _time, r_0, r_1):
		try:
			sql = {
					# 'host': '20.212.112.202',
					# 'port': 3306,
					# 'user': 'TAO',
					# 'password': 'admin',
					# 'db': 'svt'
					'host': '172.32.3.153',
					'port': 3306,
					'user': 'svt',
					'password': '1qaz@WSXiecsvt5g',
					'db': 'svt'
					}
			conn = pymysql.connect(**sql)
			cur = conn.cursor()
			sql = """INSERT INTO {table}(time, ip, phy_bler_0) VALUES(%s, %s, %s)""".format(table='phy_bler_parser')
			# sql = """INSERT INTO {table}(time, ip, phy_bler_0, phy_bler_1) VALUES(%s, %s, %s, %s)""".format(table='phy_bler_parser')
			ip = self._ip_parser()
			# print(_time, ip)
			cur.execute(sql, (_time, ip, r_0))
			# cur.execute(sql, (_time, self._ip_parser(), r_0, r_1))
			conn.commit()
		except Exception as e:
			# raise e
			pass

if __name__ == '__main__':
	bler = bler_parser()
	while True:
		r_0 = bler.parser()
		# r_0, r_1 = bler.parser()
		# mydb = infulx_db("172.32.3.196", 8086, 'admin', 'admin', 'influx')
		# mydb.write(infulx_db.get_phy_bler(r_0, r_1))
		_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
		bler.cloud_db(_time, r_0)
		# bler.cloud_db(_time, r_0, r_1)
		sleep(3)