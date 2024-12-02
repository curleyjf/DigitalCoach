import time
import os
import ast
import requests

ALL_JOBS = set()
RESULT_ENCODING = "result".encode("utf-8")
FINISHED_ENCODING = "finished".encode("utf-8")


def _update_all_jobs(redis_conn):
    keys = redis_conn.keys("*")
    for key in keys:
        key_str = key.decode("utf-8")
        if "rq:job" in key_str:
            status = redis_conn.hgetall(key)
            status = {key.decode("utf-8"): value for key, value in status.items()}
            if status["status"] == FINISHED_ENCODING:
                ALL_JOBS.add(key_str) 


def _send_job_results(redis_conn):
    print(len(ALL_JOBS)) 
    for job in ALL_JOBS:  
        result = redis_conn.hget(job, RESULT_ENCODING) 
        # b_arr = bytearray(result)
        # str_res = "".join(chr(a) for a in b_arr)
        # str_res = str_res[16:]
        # str_res = str_res[:-2]
        # parsed_res = ast.literal_eval(str_res)
        # print("parsed result here...")
        # print(parsed_res)
        # firebase_endpnt = os.getenv("FIREBASE_FUNCTIONS_ENDPOINT")
        # try:
        #     requests.post(firebase_endpnt, data=parsed_res)
        # except Exception as e:
        #     print(e)
    ALL_JOBS.clear()


def poll_connection(redis_connection):
    while True:
        print("looping...")
        _update_all_jobs(redis_connection)
        print(ALL_JOBS)
        if len(ALL_JOBS) != 0:
            _send_job_results(redis_connection)
        time.sleep(5)
