import requests
import os
import time

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

def process_contest(url):
    print("processing ", url)

    local_file_file = get_local_file_path(url)
    download_from_contest(url)


if __name__ == "__main__":
    assert os.path.exists("list.txt")
    with open("list.txt", "r") as file:
        while True:
            line = file.readline().lstrip().replace('\n','')
            if not line:
                break
            if line[0] == '#':
                continue

            process_contest(line)

