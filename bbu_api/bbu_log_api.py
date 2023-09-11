#/usr/bin/python3

from subprocess import check_output
from time import *
from configparser import ConfigParser
from math import log
import re, datetime

class bbu_log :
	def phy_log ():
		phy_list = list()
		time_parser = 'grep \""SysTimeInfo"\" \
						/home/BaiBBU_XSS/BaiBBU_PXSS/PHY/bin/Phy.log \
						| awk \'END{print $3, $4}\' | sed \'s/*//g\''
		with open('/etc/hostname', 'r+') as f:
			host_name = f.readlines()[0].strip()
		# print('hostname:', host_name)
		try:
			time_parser = check_output(time_parser, shell=True).decode("utf-8").strip()	# parser datetime
			time_parser = time_parser.split(' ')
			date = time_parser[0].replace('SysTimeInfo:', '')	# replace date
			date = date.replace('/', '-')	# for mysql date format
			time = time_parser[1].replace(',runningTime:', '')	# replace time
			time_ = date + ' ' + time
			time_=strptime(time_,'%Y-%m-%d %H:%M:%S')
			time_=int(mktime(time_))*(10**9)
		except:
			pass
		for number in range(10):	# Make sure the Cell number
			phy_parser = 'grep \"' + str(number) + ' (Kbps)\" \
						/home/BaiBBU_XSS/BaiBBU_PXSS/PHY/bin/Phy.log | \
						awk \'END{print $3,$4,$5,$6,$7,$8}\' | sed \'s/\s*$//g\''
			phy_parser = check_output(phy_parser, shell=True).decode("utf-8").strip()
			if len(phy_parser) == 0:
				break
			if '%' in phy_parser:
				phy_parser = phy_parser.replace('%', '')
				pass
			phy_list.append(phy_parser)
		for cell in range(number):	# Deal with data format
			phy_index = cell
			show_phy_str = str(phy_list[phy_index]).split(' ')	# List[Str]
			for index in range(len(show_phy_str)):
				if index == 0:
					if ',' in str(show_phy_str[0]):
						dl_tput = float(show_phy_str[0].replace(',', ''))	# Replace ',' to ''
					else:
						dl_tput = float(show_phy_str[0])
				elif index == 1:
					if ',' in str(show_phy_str[1]):
						ul_tput_1 = float(show_phy_str[1].replace(',', ''))	# Replace ',' to ''
					else:
						ul_tput_1 = float(show_phy_str[1])
				elif index == 2:
					pass
				elif index == 3:
					if ',' in str(show_phy_str[3]):
						ul_tput_2 = float(show_phy_str[3].replace(',', ''))	# Replace ',' to ''
					else:
						ul_tput_2 = float(show_phy_str[3])
				elif index == 4:
					ul_bler = float(show_phy_str[4])
				elif index == 5:
					srs_snr = int(show_phy_str[5])
					if srs_snr > 100:
						srs_snr = int(100 + log(srs_snr-100, 10))
					if srs_snr < -100:
						srs_snr*= -1
						srs_snr = int(100 + log(srs_snr-100, 10))*(-1)
				else:
					pass
			cell = str(cell)
		result={'Datetime':time_, 'HOST_NAME':host_name,'Cell':cell, 
          		'dl_tput':dl_tput, 'ul_tput_1':ul_tput_1, 'ul_tput_2':ul_tput_2,
            	'ul_bler':ul_bler, 'srs_snr': srs_snr}
		return result

#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#

	def du_log() :
		with open('/etc/hostname', 'r+') as f:
			host_name = f.readlines()[0].strip()
		cell_tail= 'grep \'cell_idx\' /home/BaiBBU_XSS/BaiBBU_SXSS/DU/bin/logs_gNB_DU | awk \'END{print $(NF)}\''
		du_tail = 'tail -n 500 /home/BaiBBU_XSS/BaiBBU_SXSS/DU/bin/logs_gNB_DU'
		cell_tail = check_output(cell_tail, shell=True).decode('utf-8').strip()
		cell_tail = cell_tail.split('[')[1].split(']')[0]
		cell_tail = int(cell_tail) + 1
		re_du = check_output(du_tail, shell=True).decode('utf-8').strip()
		# print(re_du, 're_du')

		# contentRex
		find_du_str = ''
		find_du_str = r'Timer:(\D+\d+\D+\d+\D+\d+\D+\d+\D+\d+)\D+RLC  '\
			r'UL traffic :ingress\D{1}(\d+\D+\d+)\D{1} pkt\D{1}(\d+)\D{1} '\
				r'::egress\D{1}(\d+\D+\d+)\D{1} pkt\D{1}(\d+)\D{1} \D+\d+\D+\d+\D+'\
				r'RLC  DL traffic :ingress\D{1}(\d+\D+\d+)\D{1} pkt\D{1}(\d+)\D{1} '\
					r'::egress\D{1}(\d+\D+\d+)\D{1} pkt\D{1}(\d+)\D{1} \D+\d+\D+\d+\D+RLCL '\
					r'DL traffic: um throughput\D{1}(\d+\D+\d+)\D{1} um sche cnt\D+\d+\D+am throughput\D{1}(\d+\D+\d+)\D{1} am sche cnt\D{1}\d+\D{1}\D{1}'
		contentRex = ''
		contentRex = re.findall(find_du_str, re_du)
		#print(contentRex, 'find_du_str findall')
		if len(contentRex) == 0:
			print('len(contentRex) == 0')
		for cell_number in range(int(cell_tail)):
			find_du_cell_str = ''
			find_du_cell_str = r'5GNR SYSTEM OVERVIEW AT\D+\d+\D+\d+\D+\d+\D+' + str(cell_number) + '\D.*\D+.*\D+.*\D+.*'\
					r'CRC_GOOD \D{1}(\d+)\D{1}\D+.*CRC_BAD\D{1}(\d+)\D{1}\D+.*UL_MCS_AVG\D{1}(\d+)\D{1}'\
					r'\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*PUSCH MAX DMRS PWR RBIDX\D+\d+ (\d+)\D+\d+_\d+ (\d+)\D+\d+_\d+ (\d+)\D+\d+_\d+ (\d+)\D+\d+_\d+ (\d+)\D+\d+_\d+ (\d+)\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*'\
						r'ACK\D+(\d+)\D+\D+(\d+)\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*'\
						r'UL: rank1\D{1}(\d+)\D+rank2\D{1}(\d+)\D{1} schedduled layer1\D{1}(\d+)\D{1} layer2\D{1}(\d+)\D{1}'\
							r'\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+macActiveUe\D{1}(\d+)\D{1}\D+.*\D+.*avgPrbAsgnRateDl\D+(\d+)%\D+.*\D+.*avgPrbAsgnRateUl\D+(\d+)%\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+.*\D+'\
							r'.*\D+.*\D+'\
								r'MAC DL traffic :ingress\D{1}(\d+\D+\d+)\D{1}\D+.*cell_index\D{1}(\d+)\D{1}'
			# print(find_du_cell_str)
			ind_=[x.start() for x in re.finditer('Timer', re_du)]
			contentRex_cell = ''
			contentRex_cell = re.findall(find_du_cell_str, re_du[ind_[-2]:ind_[-1]])
			#print(contentRex_cell)
			if len(contentRex_cell) == 0:
				print('len(contentRex_cell) == 0')
				break
			else:
				# contentRex
				contentRex = contentRex[:]
				len_contentRex = len(contentRex)-1
				re_contentRex = contentRex[len_contentRex]
				timerRex = re_contentRex[0]
				new_contentRex_cell = contentRex_cell[:]
				len_contentRex = len(new_contentRex_cell)-1
				re_contentRex_cell = new_contentRex_cell[len_contentRex]
				time_= strptime(timerRex, "%a %b %d %H:%M:%S %Y")
				time_=int(mktime(time_))*(10**9)
#				time_=strftime("%Y-%m-%d %H:%M:%S", time_)
		re_contentRex2=list(re_contentRex) 
		for i in range(len(re_contentRex2)): 
			try : 
				re_contentRex2[i] = int(float(re_contentRex2[i])) 
			except : 
				None
		re_contentRex_cell2=list(re_contentRex_cell)
		for i in range(len(re_contentRex_cell2)):
                        try :
                                re_contentRex_cell2[i] = int(float(re_contentRex_cell2[i]))
                        except :
                                None
		
		return {'Datetime':time_, 'HOST_NAME':host_name, 
          		'UL_Ingress':re_contentRex2[1], 'UL_Ingress_PKT':re_contentRex2[2], 
            	'UL_Egress':re_contentRex2[3], 'UL_Egress_PKT':re_contentRex2[4],
	 			'DL_Ingress':re_contentRex2[5], 'DL_Ingress_PKT':re_contentRex2[6], 
     			'DL_Egress':re_contentRex2[7], 'DL_Egress_PKT':re_contentRex2[8], 
     			'RLCL_DL_UM_Throughput':re_contentRex2[9], 'RLCL_DL_AM_Throughput':re_contentRex2[10],
        		'Cell_number':re_contentRex_cell2[19],'CRC_GOOD':re_contentRex_cell2[0], 
          		'CRC_BAD':re_contentRex_cell2[1], 'UL_MCS_AVG':re_contentRex_cell2[2], 
          		'PUSCH_PWR_0_45':re_contentRex_cell2[3], 'PUSCH_PWR_45_90':re_contentRex_cell2[4], 
            	'PUSCH_PWR_90_135':re_contentRex_cell2[5],'PUSCH_PWR_135_180':re_contentRex_cell2[6], 
             	'PUSCH_PWR_180_225':re_contentRex_cell2[7], 'PUSCH_PWR_225_273':re_contentRex_cell[8], 
     			'ACK':re_contentRex_cell2[9], 'NACK':re_contentRex_cell2[10], 'UL_RANK_1':re_contentRex_cell2[11], 
        		'UL_RANK_2':re_contentRex_cell2[12],'UL_Scheduled_Layer_1':re_contentRex_cell2[13], 
          		'UL_Scheduled_Layer_2':re_contentRex_cell2[14], 'macActiveUe':re_contentRex_cell2[15], 
            	'avgPrbAsgnRateDl':re_contentRex_cell2[16], 'avgPrbAsgnRateUl':re_contentRex_cell2[17], 
            	'MAC_DL_traffic_ingress':re_contentRex_cell2[18]}
  
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------# 

	def cu_log():
		with open('/etc/hostname', 'r+') as f:
			host_name = f.readlines()[0].strip()
		# print('hostname:', host_name)
		cu_tail = 'tail -n 100 /home/BaiBBU_XSS/BaiBBU_SXSS/CU/bin/pdcp.log'
		# cu_tail = 'tail -n 100 20220927_16_pdcp.log'
		re_cu = check_output(cu_tail, shell=True).decode('utf-8').strip()
		# contentRex
		find_cu_str = r'DL GTPU ingress traffic\D+(\d+.\d+) bps\D+(\d+.\d+)\D+Timer:(\D+\d+\D+\d+\D+\d+\D+\d+\D+\d+)\D+DL PDCP ingress traffic\D+(\d+.\d+) bps\D+egress traffic\D+(\d+.\d+) bps .*\D+UL PDCP ingress traffic\D+(\d+.\d+) bps\D+egress traffic\D+(\d+.\d+) bps .*\D+.*\D+.*\D'
		contentRex = re.findall(find_cu_str, re_cu)
		contentRex = contentRex[:]
		# print(contentRex)
		len_contentRex = len(contentRex)-1
		re_contentRex = contentRex[len_contentRex]
		# print(re_contentRex)
		timerRex = re_contentRex[2]
		# print(timerRex)
		time_= strptime(timerRex, "%a %b %d %H:%M:%S %Y")
		time_=int(mktime(time_))*(10**9)
#		time_=strftime("%Y-%m-%d %H:%M:%S", time_)
		re_contentRex2=list(re_contentRex)
		for i in range(len(re_contentRex2)):
			try :
				re_contentRex2[i] = int(float(re_contentRex2[i]))
			except :
				None
		return {'DateTime':time_, 'HOST_NAME':host_name, 
          		'DL_PDCP_Ingress':re_contentRex2[3], 'DL_PDCP_Egress':re_contentRex2[4], 
            	'UL_PDCP_Ingress':re_contentRex2[5], 'UL_PDCP_Egress':re_contentRex2[6], 
             	'DL_GTPU_Ingress':re_contentRex2[0], 'DL_GTPU_Egress':re_contentRex2[1]}
  
if __name__ == '__main__':
	bbu_log.cu_log()
