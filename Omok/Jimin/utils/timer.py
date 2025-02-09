import time 

def convert_seconds(seconds):

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60) 
    remaining_seconds = int(seconds % 60) 

    return hours, minutes, remaining_seconds

def print_duration(start_time, situation=None):
    seconds = time.time() - start_time
    h, m, s = convert_seconds(seconds)
    print(f"{situation} {h}시간 {m}분 {s}초 입니다. \n")