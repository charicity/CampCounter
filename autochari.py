import requests
import os
import time
import csv
from functools import cmp_to_key

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


def value_pk(x, y):
    if x>y:
        return -1
    if x<y:
        return 1
    return 0

def custom_sort(x, y):
    if x[0]!=y[0]:
        return value_pk(x[0], y[0]) 
    return -value_pk(x[1], y[1]) # smaller is better


def award_them(track_list, result_dict):
    track_list = sorted(track_list, key=cmp_to_key(lambda x, y: custom_sort(x[1],y[1])))
    cnt = 0
    for item in track_list:
        cnt = cnt + 1
        print(cnt,item)

        if item[0] not in result_dict:
            result_dict.update({item[0]:0})

        if cnt == 1 and item[1][0] != 0:
            result_dict[item[0]] += 10
            continue
        elif cnt == 2 and item[1][0] != 0:
            result_dict[item[0]] += 9
            continue
        elif cnt==3 and item[1][0] != 0:
            result_dict[item[0]] += 8
            continue
        else:
            if item[1][0]==0:
                result_dict[item[0]] += 1
                continue
            else:
                result_dict[item[0]] += 5
                continue


def money_calc(result_dict, track_dict, pool):
    sum = 0
    for name, score in track_dict.items():
        sum+=score
    print(pool,"/",sum,"=",pool/sum)

    for name, score in track_dict.items():
        if name not in result_dict:
            result_dict.update({name:0})
        result_dict[name] += score * pool/sum


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
        # X_score[1] == 0: 未提交
        if hasA(info) and A_score[1] != 0:
            list_A.append((info, A_score))

        B_score = get_B_score(row)
        if hasB(info) and B_score[1] != 0:
            list_B.append((info, B_score))
        
        C_score = get_C_score(row)
        if hasC(info) and C_score[1] != 0:
            list_C.append((info, C_score))
    
    print("list_A=", list_A)
    print("list_B=", list_B)
    print("list_C=", list_C)
    award_them(list_A, result_dict["A"])
    award_them(list_B, result_dict["B"])
    award_them(list_C, result_dict["C"])

def get_time_combo(row, column_solved_time, column_punish) -> int:
    solved_time = row[column_solved_time]
    if solved_time == '':
        if row[column_punish] == '':
            return 0
        return -int(row[column_punish])
    solved_time = solved_time.split(":")

    min = int(solved_time[0])*60 + int(solved_time[1])
    return min+int(row[column_punish])


def get_A_time(row) -> int:
    column_A_solved_time = 7
    column_A_punish = 8
    return get_time_combo(row, column_A_solved_time, column_A_punish)

def get_A_score(row) -> tuple:
    
    A_time = get_A_time(row)
    return (1 if A_time>0 else 0, A_time if A_time>0 else -A_time)


def get_B_time(row) -> int:
    column_B_solved_time = 9
    column_B_punish = 10
    return get_time_combo(row, column_B_solved_time, column_B_punish)

def get_B_score(row) -> tuple:
    B_time = get_B_time(row)
    return (1 if B_time>0 else 0, B_time if B_time>0 else -B_time)


def get_C_score(row) -> tuple:
    A_score = get_A_score(row)
    B_score = get_B_score(row)

    return (A_score[0]+B_score[0], A_score[1]+B_score[1])


def process_contest(url):
    print("processing ", url)

    local_file_path = get_local_file_path(url)
    download_from_contest(url)

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

    result_dict = {"A":dict(),"B":dict(),"C":dict()}
    with open("list.txt", "r") as file:
        while True:
            line = file.readline().lstrip().replace('\n','')
            if not line:
                break
            if line[0] == '#':
                continue

            process_contest(line)

    print("TRACK A: \n", result_dict["A"])
    print("TRACK B: \n", result_dict["B"])
    print("TRACK C: \n", result_dict["C"])

    prize = dict()
    money_calc(prize, result_dict["A"], 1000)
    money_calc(prize, result_dict["B"], 600)
    money_calc(prize, result_dict["C"], 400)

    print("MONEY:\n", prize)
    print("SORTED:\n",sorted(prize.items(), key=lambda item: item[1]))

    sum=0
    for name, money in prize.items():
        sum += money
    print("SUM:", sum)

