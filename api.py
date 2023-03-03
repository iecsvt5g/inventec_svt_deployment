from fastapi import FastAPI, Request, Body
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

import random, string

import os
from sys import path
import json, ast
#dirname, filename = os.path.split(os.path.abspath(__file__))
#FILE_PATH = dirname.split("/")
#FILE_PATH[-1]=""
#BASE_PATH = "/".join(str(x) for x in FILE_PATH)
path.append("/etc/iev_svt_deployment")
#from mybbu import  *
import subprocess
import asyncio
#from loguru import logger
from functools import wraps
from asyncio import ensure_future
from starlette.concurrency import run_in_threadpool
from typing import Any, Callable, Coroutine, Optional, Union
from time import sleep
import time,datetime , socket

import logging


####            ####
#### Settings   ####
####            ####
## DEFAULT VALUE
DEFAULT_PORT = 8877
LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG
LOG_FILE  = './server.log'
MYBBU = {}


# API SETTINGS
IEC_5G_EMAIL = "CCS5G_support@inventec.com"
IEC_5G_URL   = "http://5G.inventec.com/"
IEC_5G_NAME  = "Inventec 5G Soluation"
IEC_5G_API_VERSION = "0.0.1"
IEC_5G_DESCRIPTION = "inventec ran api"
IEC_5G_TITLE = "Inventec RAN API"

## LOG
# setup loggers
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
#fh = logging.FileHandler(filename='./server.log')
fh = logging.FileHandler(filename=LOG_FILE)
formatter = logging.Formatter(    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch) # Show log on monitor
logger.addHandler(fh) # Save log to file

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


def run_command(command):
    result = ""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
#        print(">>1 result,",result)
        result = result.stdout
#        print(">>2 result,",result)
#        result = result.replace("'", '"')
#        print(">>3 result,",result)
        result = result.strip()
#        print(">>4 result,",result,type(result))
#    json_result = json.loads(result)
        result = eval(result)
#        result = ast.literal_eval(result)
#        print(">>5 result,",result)
    except Exception as e:
        print("ERROR : ", e)
    return result

#run_command("./mybbu -h")

####        ####
#### task   ### (for schedule task)
####        ####
NoArgsNoReturnFuncT = Callable[[], None]
NoArgsNoReturnAsyncFuncT = Callable[[], Coroutine[Any, Any, None]]
NoArgsNoReturnDecorator = Callable[
    [Union[NoArgsNoReturnFuncT, NoArgsNoReturnAsyncFuncT]],
    NoArgsNoReturnAsyncFuncT
]
def repeat_task(
    *,
    seconds: float,
    wait_first: bool = False,
    raise_exceptions: bool = False,
    max_repetitions: Optional[int] = None,
) -> NoArgsNoReturnDecorator:

    def decorator(func: Union[NoArgsNoReturnAsyncFuncT, NoArgsNoReturnFuncT]) -> NoArgsNoReturnAsyncFuncT:
        is_coroutine = asyncio.iscoroutinefunction(func)
        had_run = False

        @wraps(func)
        async def wrapped() -> None:
            nonlocal had_run
            if had_run:
                return
            had_run = True
            repetitions = 0

            async def loop() -> None:
                nonlocal repetitions
                if wait_first:
                    await asyncio.sleep(seconds)
                while max_repetitions is None or repetitions < max_repetitions:
                    try:
                        if is_coroutine:
                            # 以协程方式执行
                            await func()  # type: ignore
                        else:
                            # 以线程方式执行
                            await run_in_threadpool(func)
                        repetitions += 1
                    except Exception as exc:
                        print('Error In task: {exc}')
                        if raise_exceptions:
                            raise exc
                    await asyncio.sleep(seconds)
            ensure_future(loop())
        return wrapped
    return decorator

####            ####
#### Fast API   ####
####            ####
RESULT_NOT_FOUND = {"message":"Error , result not found"}
#mydb = infulx_db("localhost",8086,'admin','admin','influx') # in host : localhost
myItem = {}
favicon_path = 'favicon.ico'
bbu_dict = {}
bbu_ip = get_ip()
#bbu = MyBbu(bbu_ip)

## Start APP Service
app = FastAPI(
    title = IEC_5G_TITLE,
    description = IEC_5G_DESCRIPTION,
    version = IEC_5G_API_VERSION,
    contact = {
        "name":  IEC_5G_NAME,
        "url":   IEC_5G_URL,
        "email": IEC_5G_EMAIL,
    },
)
#app.mount("/static", StaticFiles(directory="static"), name="static")

# log
@app.middleware("http")
async def log_requests(request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    return response

# GET   /
@app.get("/status")
async def status():
    return {"status": "alive"}

# GET /docs
@app.get("/docs", include_in_schema=False)
async def overridden_swagger():
    icon = "https://ebg.inventec.com/resources/_img/favicon.ico"
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Inventec API", swagger_favicon_url= icon )

##
## Schedule Task
##
# POST  trigger BBU to update datas
@app.on_event('startup')
@repeat_task(seconds=77, wait_first=True)
def repeat_task_aggregate_request_records() -> None:
    # Every 45 sec to update bbu informations.
    tasks = ["bmc"]
    for t in tasks:
#        MYBBU[t.upper] = ""
        print("./mybbu --{0}".format(t))
        MYBBU["{0}".format(t.upper())] = run_command("./mybbu --{0}".format(t) )
    print("- ",MYBBU)
    logger.debug(f'== Long Schedule Task: Update ',time.time())

@app.on_event('startup')
@repeat_task(seconds=34, wait_first=True)
def schedule_task2() -> None:   # 5 sec schedule task
    tasks = ["service","alarm","system","ru","acc","bler"]
    for t in tasks:
        print("./mybbu --{0}".format(t))
        MYBBU["{0}".format(t.upper())] = run_command("./mybbu --{0}".format(t))
    print('== Schedule Task2: Update ',time.time())

##
## APIs
##
@app.put("/update", tags=["BBU"])
async def update():
    logger.debug(f"BBU Update")
    tasks = ["service","alarm","system","ru","acc","bler","bmc"]
    for t in tasks:
        print("./mybbu --{0}".format(t))
        MYBBU["{0}".format(t.upper())] = run_command("./mybbu --{0}".format(t))

    return True


## Operations
@app.post("/service/start", tags=["BBU"])
def start():
    logger.debug(f"BBU Start")
    return run_command("./mybbu --start")

@app.post("/service/stop", tags=["BBU"])
def stop():
    logger.debug(f"BBU Stop")
    return run_command("./mybbu --stop")

@app.post("/service/restart", tags=["BBU"])
def restart():
    logger.debug(f"BBU Restart")
    return run_command("./mybbu --restart")

# GET BBU information
@app.get("/info", tags=["BBU"])
def info():
    print("- ",MYBBU)
    return MYBBU

# GET Service
@app.get("/service/status", tags=["BBU"])
def service():
    print("- ",MYBBU)
    return MYBBU.get("SERVICE")

# GET Alarm
@app.get("/alarm", tags=["BBU"])
def alarm():
    print("- ",MYBBU)
    return MYBBU.get("ALARM")

# GET BMC
@app.get("/bmc", tags=["BBU"])
def bmc():
    return MYBBU.get("BMC")

# GET ru
@app.get("/ru", tags=["BBU"])
def ru():
    return MYBBU.get("RU")

# GET acc
@app.get("/acc", tags=["BBU"])
def acc():
    return MYBBU.get("ACC")

# GET sys_info
@app.get("/sys_info", tags=["BBU"])
def sys_info():
    return MYBBU.get("SYSTEM")

# GET bler
@app.get("/bler", tags=["BBU"])
def bler():
    return MYBBU.get("BLER")

if __name__ == "__main__":
    import uvicorn
    logger.debug(f"== API SERVICE START ==")
    logger.info(f"== API SERVICE START ==")
    logger.warning("== API SERVICE START ==")
    uvicorn.run(app='api:app', host="0.0.0.0", port=DEFAULT_PORT, reload=False)
    # http://172.32.3.216:8087/docs
    # http://172.32.3.216:8087
