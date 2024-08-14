import requests
import os
import time
import csv

banlist = set()

def hasA(string) -> bool:
    return string.find("A")!=-1
def hasB(string) -> bool:
    return string.find("B")!=-1
def hasC(string) -> bool:
    return string.find("C")!=-1
def hasD(string) -> bool:
    return string.find("D")!=-1

def is_legit_track(string) -> bool:
    if string == '':
        return False
    
    if hasA(string) and hasB(string):
        return False
    
    if hasD(string):
        return False
    
    if (not hasA(string) and not hasB(string)) and hasC(string):
        print("Warning: this guy only has C")
        return True
    return True

def extract_chinese(string) -> str:
    res = ''
    for c in string:
        if '\u4e00' <= c <= '\u9fff':
            res = res + c
    return res

def extract_id(string) -> str:
    res = ''
    for c in string:
        if '0'<=c<='9':
            res = res + c
    return res

# if track is not legit, return ''
def extract_track(string) -> str:
    res = ''
    for c in string:
        if 'A'<=c<='C':
            res = res + c
        if 'a'<=c<='c':
            res = res + str.upper(c)
    track = ''.join(sorted(res))

    if is_legit_track(track) == False:
        return ''
    return track # that's good

def download_from_contest(url):
    print("downloading ", url, end=' ')
    local_file_file = get_local_file_path(url)
    remote_down_path = url + "/export/csv"

    if os.path.exists(local_file_file):
        print("skipped")
        return

    down_res = requests.get(remote_down_path)
    with open(local_file_file,'wb') as file:
        file.write(down_res.content)
    
    print("done")
    print("sleeping for 21s due to the speed limitation of hydro")
    time.sleep(21)


def get_local_file_path(url) -> str:
    arr = url.split("/")
    assert arr

    local_file_file = "./down_csv/"+arr[len(arr)-1]+".csv"
    return local_file_file



def read_local_csv(file_path) -> list:
    print("reading csv", file_path)
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar=' ')

        result = []
        cnt = 0
        for row in spamreader:
            if cnt == 0:
                cnt = 1
                continue
            result.append(row)
    return result

def get_info_from_cell(cell) -> str:
    assert type(cell) == str
    name_cn = extract_chinese(cell)
    track = extract_track(cell)
    # id = extract_id(cell) # temporarily dont need to read id
    if track=='' or name_cn=='':
        return ''
    # print(track,name_cn)
    return track+name_cn

def get_info(row) -> str:
    column_userid = 1
    column_alias = 4
    column_info = 5

    result = ''

    result = get_info_from_cell(row[column_info])
    if result != '':
        return result
    
    result = get_info_from_cell(row[column_alias])
    if result != '':
        return result
    
    result = get_info_from_cell(row[column_userid])
    if result != '':
        return result
    return result

def process_local_csv(file_path, result_dict):
    raw_rows = read_local_csv(file_path)

    list_A = []
    list_B = []
    list_C = []
    for row in raw_rows:
        info = get_info(row)
        print(info,"<---",row)
        if info == '' or info in banlist:
            continue
        
        A_score = get_A_score(row)
        if hasA(info) and A_score[1] != 0:
            list_A.append((info, A_score))

        B_score = get_B_score(row)
        if hasB(info) and B_score[1] != 0:
            list_B.append((info, B_score))
        
        C_score = get_C_score(row)
        if hasC(info) and C_score[1] != 0:
            list_C.append((info, C_score))
    
    print("list_A=",list_A)
    print("list_B=",list_B)
    print("list_C=",list_C)

def get_time_combo(row, column_solved_time, column_punish) -> int:
    solved_time = row[column_solved_time]
    if solved_time == '':
        return -1
    solved_time = solved_time.split(":")

    min = int(solved_time[0])*60 + int(solved_time[1])
    return min+int(row[column_punish])


def get_A_time(row) -> int:
    column_A_solved_time = 7
    column_A_punish = 8
    return get_time_combo(row, column_A_solved_time, column_A_punish)

def get_A_score(row) -> tuple:
    A_time = get_A_time(row)
    return (1 if A_time!=-1 else 0, max(A_time, 0))


def get_B_time(row) -> int:
    column_B_solved_time = 9
    column_B_punish = 10
    return get_time_combo(row, column_B_solved_time, column_B_punish)

def get_B_score(row) -> tuple:
    B_time = get_B_time(row)
    return (1 if B_time!=-1 else 0, max(B_time, 0))


def get_C_score(row) -> tuple:
    A_score = get_A_score(row)
    B_score = get_B_score(row)

    return (A_score[0]+B_score[0], A_score[1]+B_score[1])


def process_contest(url):
    print("processing ", url)

    local_file_path = get_local_file_path(url)
    download_from_contest(url)

    result_dict = {"a":dict(),"b":dict(),"c":dict()}

    process_local_csv(local_file_path, result_dict)


def read_ban_list():
    print("reading ban list")
    if not os.path.exists("./banlist.txt"):
        print("not existed, skipped")
        return

    with open("./banlist.txt", "r", encoding="utf-8") as file:
        while True:
            line = file.readline().lstrip().replace('\n','')
            if not line:
                break
            if line[0] == '#':
                continue
            banlist.add(line)
    print("banlist:", banlist)

if __name__ == "__main__":
    read_ban_list()
    assert os.path.exists("list.txt")
    with open("list.txt", "r") as file:
        while True:
            line = file.readline().lstrip().replace('\n','')
            if not line:
                break
            if line[0] == '#':
                continue

            process_contest(line)

