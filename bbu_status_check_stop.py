#/usr/bin/python3
'''
Created on 2022/08/25

@author: ZL Chen
@title: BBU status check.
'''

import sys, subprocess, pymysql, time
# sys.path.insert(0, '/root/automation/suite/linux/lib')
sys.path.insert(0, '/etc/inventec_svt_deployment')
# # from gmail_notify import gmail_notify
from line_notify import line_notify
from datetime import datetime
# from influx_db import infulx_db
from subprocess import check_output

class bbu_check(object):
	def log(self):
		print("BBU is stopped.")
		ip = self.notify()
		return self.bbu_status, ip

	def notify(self):
		# g_n = gmail_notify()
		l_n = line_notify()
		result = datetime.now().strftime("%Y-%m-%d %H:%M:%S %p")
		# _ip = subprocess.check_output('ip address show enp0s20f0u2 | grep \"inet \" | awk {\'print $2\'}', shell=True)
		# ip = str(_ip[0:-4]).split('b')[1]
		ip = self._ip_parser()
		print('ip = ' + ip)
		message = 'BBU is stopped.\n' + 'ip = ' + str(ip) + '\n' + result
		# g_n.gmail('iecsvt5g@gmail.com', 'Chen.ZL@inventec.com, iec100535@gmail.com', message)
		l_n.send_message(message)
		self.bbu_status = 0
		return ip

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

	def cloud_db(self, _time, ip, bbu_status):
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
			sql = """INSERT INTO {table}(time, ip, bbu_status) VALUES(%s, %s, %s)""".format(table='bbu_status')
			# cur.execute(sql, (_time, '172.32.3.155', r_0))
			# cur.execute(sql, (_time, '172.32.3.155', str(bbu_status)))
			cur.execute(sql, (_time, ip, str(bbu_status)))
			conn.commit()
		except Exception as e:
			raise e

if __name__ == '__main__':
	bbu_status_check = bbu_check()
	# mydb = infulx_db("172.32.3.196", 8086, 'admin', 'admin', 'influx')
	status_check, ip = bbu_status_check.log()
	# mydb.write(infulx_db.get_bbu_status(status_check))
	_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
	bbu_status_check.cloud_db(_time, ip, status_check)
