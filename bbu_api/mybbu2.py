import paramiko
import subprocess
import socket
import re,time,datetime
import urllib.request
import concurrent.futures
import psutil,math
import argparse
import asyncio
BBU_USER = "root"
BBU_PASSWORD = "inventec"
BBU_WEB_USER     = "admin"
BBU_WEB_PASSWORD = "admin"
RU_USER      = "root"
RU_PASSWORD  = "root123"

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    return result.stdout


def ssh_and_exec_cmd(command, server, server_username, server_pass):
    # SSH to host and execut command
    try:
        #print("SSH Start,",server,command)
        LOCK=False
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=server_username, password=server_pass, timeout=10)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        ssh_stdin.write(server_pass + "\n")
        result = ssh_stdout.read().decode("utf-8")
        ssh_stdin.flush()
    except:
#        print("SSH Connext error,",server,command)
        result = "Error"
    finally :
        ssh.close()
        #print("END SSH")
    return result


async def ssh_twice_cmd(TEST_CMD,FIRST_IP, FIRST_USER, FIRST_PW, SECOND_IP, SECOND_USER, SECOND_PW):
    # SSH to host1 and ssh to host2 and execute command
    result = False
    try:
        first_host = paramiko.SSHClient()
        second_host = paramiko.SSHClient()
        first_host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        first_host.connect(FIRST_IP, username=FIRST_USER, password=FIRST_PW, timeout=10)
        first_hosttransport = first_host.get_transport()
        dest_addr  = (SECOND_IP, 22) #edited#
        local_addr = (FIRST_IP, 22) #edited#
        first_hostchannel = first_hosttransport.open_channel("direct-tcpip", dest_addr, local_addr)
        second_host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        second_host.connect(SECOND_IP, sock=first_hostchannel,  username=SECOND_USER, password=SECOND_PW,  timeout=10)

        stdin, stdout, stderr = second_host.exec_command(TEST_CMD)
        result = stdout.read()
    except:
 #       print("Error: ssh_twice_cmd ")
        pass
    finally :
        if second_host:
            second_host.close()
        if first_host:
            first_host.close()
        return result

####        ####
#### UTIL   ####
####        ####
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def checkRE(pats,txt):
    for pat in pats:
        txt = re.search(pat,str(txt))
        if(txt):
            txt = str(txt.group())
        else:
            txt = False
    return txt if txt else False

def space_str_to_list_format(l):
    l = l.split(" ")
    while '' in l:
        l.remove('')
    return l


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False



####                ####
#### BBU modules    ####
####                ####

## SystemInformation Class
class SystemInformation:
    def __init__(self):
        self.info = {}
        self.info['cpu'] = {}
        self.info['memory'] = {}
        self.info['disk'] = {}
        self.info['network'] = {}
        self.info['boot_time'] = 0
        self.info['dhcp_is_up'] = False

    def update(self):
        self.info['boot_time'] = psutil.boot_time()
        self.info["dhcp_is_up"] = self.check_dhcp_service()

        self.info['cpu']['count'] = psutil.cpu_count(logical=False)
        self.info['cpu']['percent'] = psutil.cpu_percent()
        self.info['cpu']['idle'] = psutil.cpu_times().idle

        memory_info = psutil.virtual_memory()
        self.info['memory']['total'] = self.bytes_to_human_readable(memory_info.total)
        self.info['memory']['available'] = self.bytes_to_human_readable(memory_info.available)
        self.info['memory']['used'] = self.bytes_to_human_readable(memory_info.used)
        self.info['memory']['percent'] = memory_info.percent

        disk_info = psutil.disk_usage('/')
        self.info['disk']['total'] = self.bytes_to_human_readable(disk_info.total)
        self.info['disk']['used'] = self.bytes_to_human_readable(disk_info.used)
        self.info['disk']['free'] = self.bytes_to_human_readable(disk_info.free)
        self.info['disk']['percent'] = disk_info.percent

        io_counters = psutil.net_io_counters()
        self.info['network']['bytes_sent'] = self.bytes_to_human_readable(io_counters.bytes_sent)
        self.info['network']['bytes_recv'] = self.bytes_to_human_readable(io_counters.bytes_recv)

    def bytes_to_human_readable(self, num_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num_bytes < 1024.0:
                return f"{num_bytes:.2f} {unit}"
            num_bytes /= 1024.0

    def check_dhcp_service(self):
        command = "systemctl status dhcpd.service"
        output = subprocess.check_output(command.split())
        output_str = output.decode("utf-8")
        if "active (running)" in output_str:
            return True
        else:
            return False

## BMC Class
class Bmc(object):
    def __init__(self,bbu_ip='172.32.3.155'):
        self.bbu_ip  = bbu_ip
        self.sdr = {"TOTAL_PWR":0.0,'CPU0_TEMP': 0.0, 'CPU1_TEMP': 0.0,
                    'FAN0': 0.0, 'FAN1': 0.0, 'FAN2': 0.0, 'FAN3': 0.0, 'FAN4':0.0,'FAN5': 0.0,'FAN6': 0.0}

    def __str__(self):
        return "BMC INFO :BBU IP : {}".format(self.bbu_ip )

    def __ipmi_sdr_to_dict(self, ipmi_sdr):
        result={}
        sdr_lines = ipmi_sdr.split("\n")
        for sdr in sdr_lines:
            ss = sdr.replace(" ","")
            ssdr= ss.split('|')
            if(len(ssdr)>= 3):
                result[ssdr[0].upper()]=  float(checkRE(['-*\d+\.*\d*'],ssdr[1]) )# "status":ssdr[2]
        return result

    def update_sdr(self):
        cmd = "ipmitool sdr"
        try:
            ipmi_sdr = run_command(cmd)
            self.sdr = self.__ipmi_sdr_to_dict(ipmi_sdr)
        except:
            #print("ERROR, UPDATE SDR ERROR!!")
            pass

    def update(self):
        self.update_sdr()


## Acc Card Class
class AccCard(object):
    def __init__(self,bbu_ip='172.32.3.155',acc_ip="0.0.0.0",acc_mac=""):
        self.acc_ip  = acc_ip
        self.acc_mac = acc_mac
        self.bbu_ip  = bbu_ip
        self.status  = ""
        self.temperature = -1
        self.power = -1

    def __str__(self):
        return "  ACC Card : {}, temp = {}\n".format(str(self.acc_ip),str(self.temperature))

    def get_temperature(self):
        # Get ACC Card temperature
        command = 'ru_cmd gettemp | sed \'s/[a-z]*//g\' | tr -d \':\''
        try:
            t = int( ssh_and_exec_cmd(command, self.acc_ip, RU_USER, RU_PASSWORD) )
        except:
            t = -1
        return int(t)

    def get_total_walt(self):
        command = 'ru_cmd gettotalpower'
        try:
            t = ssh_and_exec_cmd(command, self.ru_ip, RU_USER, RU_PASSWORD)
            s = t.decode()
            r = checkRE(["total power \d+.\d W","\d+.\d"],s)
        except:
            r = -1
        return float(r)

    def update(self):
        self.temperature = self.get_temperature()
        self.power = self.get_total_walt()

    def get(self):
        return {"IP":self.acc_ip,
                "MAC":self.acc_mac,
                "BBU":self.bbu_ip,
                "STATUS":self.status,
                "TEMPERATURE":self.temperature,
                "POWER":self.power}


##  RU Class
class RadioUnit(object):
    def __init__(self,bbu_ip='172.32.3.155',ru_ip="",ru_mac=""):
        self.bbu_ip = bbu_ip
        self.ru_mac = ru_mac
        self.ru_ip = ru_ip
        self.status  = ""
        self.temperature = -1

    def __str__(self):
        return "  RU : {}, \n".format(str(self.ip))

    def get_temperature(self):
        command = "ru_cmd p radio"
        t = -1
        try:
            r = ssh_and_exec_cmd('ru_cmd p radio', self.ru_ip, RU_USER, RU_PASSWORD)
            t = 0
            if(r):
#                s = r.decode()
                s=r
                ss = s.split("\n")
                for i in [3,4,5,6]:
                    t += int(space_str_to_list_format(ss[i])[-2])
                t = t/4
        except:
            #print("ERROR, GET RU TEMP FAIL")
            t = -1
        return float(t)

    def update(self):
        self.temperature = self.get_temperature()

    def get(self):
        return {"IP":self.ru_ip,
                "MAC":self.ru_mac,
                "BBU":self.bbu_ip,
                "STATUS":self.status,
                "TEMPERATURE":self.temperature}


## BBU Class
class MyBbu(object):

    def __init__(self,ip='172.32.3.155'):
        #print("BBU:",ip)
        self.ip  = ip
        self.bmc = Bmc(ip)
        self.acc_card = {}
        self.rus = {}
        self.alarm = {}
        self.service = {}
        self.restart_time = 0
        self.last_update = 0
        self.sys_info = SystemInformation()
        self.bler = {}

    def __str__(self):
        return "BBU IP : {}, \nRUS {}\n, Acc: {}".format(self.ip,str(self.rus), str(self.acc_card) )

    def __update_dev_list(self):
        arp_list = False
        IPList = []
        fs = []
        # Update ACC & RU List
        BBU_GET_IPS_CMD = "arp -n |grep -Fv incomplete  | grep xeth  |awk '{print $1 ,$3}'"
        try:
            arp_list = run_command(BBU_GET_IPS_CMD)
        except:
            print("[ran_info_dev.py] SSH Error ,",self.ip)
            return False
        if(arp_list):
            for str_line in arp_list.split("\n"):
                mystr = str_line.replace("(","").replace(")","")
                ip = mystr.split(" ")[0]
                if( valid_ip(ip) ):
                    mac = mystr.split(" ")[1]
                    result = str(ssh_and_exec_cmd("cat /etc/banner",ip, RU_USER, RU_PASSWORD))
                    if( result.find("RRU")>= 0):        # RU
                        self.rus[ip] = RadioUnit(self.ip, ip, mac)
                    elif( result.find("Acc")>= 0):      # ACC
                        self.acc_card[ip] = AccCard(self.ip, ip, mac)
                    else:
                        pass
        if(len(self.rus) == 0 ):
            self.rus["0.0.0.0"] = RadioUnit(self.ip, "0.0.0.0","")
        if(len(self.acc_card) == 0):
            self.acc_card["0.0.0.0"] = AccCard(self.ip, "0.0.0.0","")
        return True

    def __update_dev_info(self):
        # Update ACC/RU info
        for k,a in self.acc_card.items():
            a.update()
        for k,r in self.rus.items():
            r.update()
        return True

    def __alarm_formatter(self,alarms_str,status=""):
        result = []
        if(alarms_str == "Object Not Found"):
            return result
        alarms_list = alarms_str.split("#")
        for alarm in alarms_list:
            alarm_format={"ALARM_STAUTS":status}
            pats=[ r'FAP.0.TR196_(HISTORY_EVENT|CURRENT_ALARM)..+: ','.\d+:', r'\d+']
            id =  checkRE(pats,alarm)
            alarm_format["ID"] = id
            pats=[ r'ALARM_PERCEIVED_SEVERITY:=\d ',r'\d+']
            severity = checkRE(pats,alarm)
            int_cols = ["ALARM_RAISED_TIME","ALARM_PERCEIVED_SEVERITY","ALARM_IDENTIFIER","ALARM_CHANGED_TIME","ALARM_EVENT_TIME","ALARM_EVENT_TYPE","TR069_FER_SEQUENCE_NUMBER"]
            for col in int_cols:
                pats=[ r'{0}:=\d+ '.format(col),r'\d+']
                r = checkRE(pats,alarm)
                alarm_format[col] = r
            quot_cols = ["ALARM_PROBABLE_CAUSE","ALARM_SPECIFIC_PROBLEM","ALARM_FAULT_LOCATION","ALARM_ADDITIONAL_TEXT","ALARM_INTERNAL_SERIAL_NUM"]
            for col in quot_cols:
                pats=[ r'{0}:=\"([^\"]*)\" '.format(col),r'\"([^\"]*)\"']
                r = checkRE(pats,alarm)
                alarm_format[col] = r
            result.append(alarm_format)
        return result

    def __update_alarm_infos(self):
        url =  "http://{}/utility/get_alarm_infos.sh".format(self.ip)
        req = urllib.request.Request(url, {})
        try:
            with urllib.request.urlopen(req) as response:
                result = response.read()
            result = result.decode("utf-8").split("\n")
            act_alarm =  result[0]
            his_alarm = result[2]
            #print(act_alarm,"\n",his_alarm)
            self.alarm =  {"CURRENT_ALARM" : self.__alarm_formatter(act_alarm,"CURRENT_ALARM"),
                           "HISTORY_EVENT": self.__alarm_formatter(his_alarm,"HISTORY_EVENT") }
            return True
        except:
            return False

    def __update_service_is_up(self):
        cmds = [ "l1app","du_layer2", "gnb_cu_pdcp"]
        str_cmd = ""
        for cmd in cmds:
            str_cmd += " ps aux --sort -%cpu | head -8 | grep -E '{0}' | wc -l;".format(cmd)
        result={'l1app': 0, 'du_layer2': 0, 'gnb_cu_pdcp': 0}
        self.service = result
        try:
            res=[]
            bbu_service = run_command(str_cmd)
            if(bbu_service):
                for str_line in bbu_service.split("\n"):
                    status = str_line.isdigit()
                    if(status):
#                        res.append(True if int(str_line) > 0 else False)  # Count > 0 is True  <=0 is False
                        res.append(int(str_line)) # count
                result = dict(zip(cmds, res ))
            self.service = result
            return True
        except:
#            print("Error ")
            return False
    """
    def __check_bbu_status(self):
        cmds = [ "l1app","du_layer2", "gnb_cu_pdcp"]
        str_cmd = ""
        for cmd in cmds:
            str_cmd += " ps aux --sort -%cpu | head -8 | grep -E '{0}' | wc -l;".format(cmd)
        result={'l1app': 0, 'du_layer2': 0, 'gnb_cu_pdcp': 0}
        try:
            res=[]
            bbu_service = run_command(str_cmd)
            if(bbu_service):
                for str_line in bbu_service.split("\n"):
                    status = str_line.isdigit()
                    if(status):
                        res.append(int(str_line))
                result = dict(zip(cmds, res ))
                return result
        except:
#            print("Error ")
            pass
        return result
    """
    def __update_bler(self):
        cmd = "tail -n 600 /home/BaiBBU_XSS/BaiBBU_PXSS/PHY/bin/Phy.log"
        last_bler = {}
        try:
            logs = run_command(cmd)
            myreg = r"l1app SysTimeInfo:(\d+\/\d+\/\d+ \d+:\d+:\d+),.*\D+PCI((\D+(\d+) \(Kbps\) +(\d{0,3},?\d{0,3}) +(\d{0,3},?\d{0,3}) \/ +(\d{0,3},?\d{0,3}) +(\d{0,3}.?\d{0,3})% +-?\d{1,3} dB +4T4R +\d+){1,5})"
            mre2 = r"(\D+(\d+) \(Kbps\) +(\d{0,3},?\d{0,3}) +(\d{0,3},?\d{0,3}) \/ +(\d{0,3},?\d{0,3}) +(\d{0,3}.?\d{0,3})% +-?\d{1,3} dB +4T4R +\d+)"
            pat  = re.compile(myreg)
            pat2 = re.compile(mre2)
            txt = """ """
            one_log = pat.findall(logs)
            for i in one_log:
                ts = i[0]
                ts = time.strptime(ts,'%Y/%m/%d %H:%M:%S')
                ts = datetime.datetime.utcfromtimestamp( time.mktime(ts)  )  - datetime.timedelta(hours=8)
                r2 = pat2.findall(i[1])
                for j in r2:
                    pci = j[1]
                    bler = j[5]
                    last_bler[ts] = {"time":ts, "pci":pci, "bler":bler}
#                    print({"time":ts, "pci":pci, "bler":bler})
            self.bler = last_bler
        except:
            #print("ERROR, Update bler")
            pass

    ## Public Function
    # ALL
    def get(self):
        result = {}
        result["IP"] = self.ip
        result["ACC"] = self.get_acc()
        result["RU"] = self.get_ru()
        result["ALARM"] = self.get_alarm()
        result["BMC"] = self.get_bmc()
        result["LAST_UPDATE"] = self.last_update
        result["BLER"] = self.bler
        result["SYSTEM"] = self.sys_info.info
        return result

    def update(self):
        self.update_acc_ru()
        self.update_alarm()
        self.update_service()
        self.update_bmc()
        self.update_sys_info()
        self.update_bler()
        self.last_update = time.time()
        return True

    # Acc, RU
    def get_ru(self):
        result = {}
        for k,ru in self.rus.items():
            result[k] = ru.get()
        return result

    def get_acc(self):
        result = {}
        for k,acc in self.acc_card.items():
            result[k] = acc.get()
        return result

    def update_acc_ru(self):
        self.__update_dev_list()
        self.__update_dev_info()
        return True

    # Alarm
    def get_alarm(self):
        return self.alarm

    def update_alarm(self):
        return self.__update_alarm_infos()

    # Service
    def get_service(self):
        return self.service

    def update_service(self):
        return self.__update_service_is_up()

    # BMC
    def get_bmc(self):
        return self.bmc.sdr

    def update_bmc(self):
        return self.bmc.update()

    # Sys Info
    def get_sys_info(self):
        return self.sys_info.info

    def update_sys_info(self):
        self.sys_info.update()
        return True

    # Bler
    def get_bler(self):
        return self.bler

    def update_bler(self):
        self.__update_bler()
        return True

    ## Operations
    def start_bbu(self):
        bbu_status = self.__check_bbu_status()
        for status in bbu_status.values():
            if (status > 0): return "BBU is still running"
        #print("Starting BBU")
        BBU_start_CMD = "cd ~ && nohup ./BBU start >/dev/null 2>&1 &"
        try:
            bbu_start = run_command(BBU_start_CMD)
            self.restart_time = time.time()
            #print(bbu_start)
            return True
        except:
            #print("BBU start SSH Error ,",self.ip)
            return False

    def restart_bbu(self):
        if time.time() - self.restart_time < 5 * 60:
            return "BBU is restarting"
        #print("Restarting BBU")
        BBU_restart_CMD = "cd ~ && ./BBU restart >/dev/null 2>&1 &"
        try:
            bbu_restart = run_command(BBU_restart_CMD)
            self.restart_time = time.time()
            #print(bbu_restart)
            return True
        except:
            #print("BBU restart SSH Error ,",self.ip)
            return False
        if(bbu_restart):
            print(bbu_restart)

    def stop_bbu(self):
        bbu_status = self.__check_bbu_status()
        all_status = 0
        for status in bbu_status.values():
            all_status += status
        if (all_status == 0): return "BBU has stopped"
        print("Stopping BBU")
        BBU_stop_CMD = "cd ~ && ./BBU stop"
        try:
            bbu_stop = run_command(BBU_stop_CMD)
            print(bbu_stop)
            return True
        except:
            print("BBU stop SSH Error ,",self.ip)
            return False

def main():
    parser = argparse.ArgumentParser(description='Send AT Help')
    group = parser.add_mutually_exclusive_group()
    group.add_argument( "--all", action="store_true",  help="BBU all information")
    group.add_argument( "--service", action="store_true",  help="BBU Service")
    group.add_argument( "--alarm", action="store_true",  help="alarm ")
    group.add_argument( "--ru", action="store_true",  help="ru ")
    group.add_argument( "--acc", action="store_true",  help="acc ")
    group.add_argument( "--system", action="store_true",  help="system ")
    group.add_argument( "--bmc", action="store_true",  help="bmc ")
    group.add_argument( "--bler", action="store_true",  help="bler")
    group.add_argument( "--start", action="store_true",  help="start ")
    group.add_argument( "--stop", action="store_true",  help="stop ")
    group.add_argument( "--restart", action="store_true",  help="restart ")
    args = parser.parse_args()

    bbu_ip = get_ip()
    bbu = MyBbu(bbu_ip)

    # BBU all
    if args.all:
        bbu.update()
        print( bbu.get())
#        print("ALL")
    # BBU Service
    if args.service:
        bbu.update_service()
        print( bbu.get_service() )
#        print("service")
    # BBU Alarm
    if args.alarm:
        bbu.update_alarm()
        print( bbu.get_alarm() )
#        print("alarm")
    # RU
    if args.ru:
        bbu.update_acc_ru()
        print(bbu.get_ru())
#        print("ru")
    # Acc
    if args.acc:
        bbu.update_acc_ru()
        print(bbu.get_acc())
#        print("acc")
    # BMC
    if args.bmc:
        bbu.update_bmc()
        print(bbu.get_bmc())
#        print("bmc")
    # System
    if args.system:
        bbu.update_sys_info()
        print(bbu.get_sys_info())
#        print("system")
    # Bler
    if args.bler:
        bbu.update_bler()
        print(bbu.get_bler())
    # Start
    if args.start:
        bbu.start_bbu()
#        print("start")
    # Stop
    if args.stop:
        bbu.stop_bbu()
#        print("stop")
    # restart
    if args.restart:
        bbu.restart_bbu()
#        print("restart")


    return 0

    #parser = argparse.ArgumentParser(description='BBU Command line tool Help')

if __name__ == '__main__':
    main()

