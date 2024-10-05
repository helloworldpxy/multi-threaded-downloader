import os
import requests
from threading import Thread
from queue import Queue
from tqdm import tqdm
 
# 下载设置
url = "https://example.com/largefile.zip"  # 替换为你要下载的文件URL
filename = "largefile.zip"
num_threads = 4  # 线程数
 
# 获取文件大小
try:
    response = requests.head(url)
    response.raise_for_status()  # 检查请求是否成功
    file_size = int(response.headers['Content-Length'])
except requests.RequestException as e:
    print(f"获取文件大小失败: {e}")
    exit(1)
 
# 创建队列
queue = Queue()
 
# 分块下载
def download_chunk(start, end):
    """
    下载文件的指定块。
     
    参数:
    start - 块的起始字节
    end - 块的结束字节
    """
    headers = {'Range': f'bytes={start}-{end}'}
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(filename, "r+b") as f:
            f.seek(start)
            f.write(response.content)
    except requests.RequestException as e:
        print(f"下载失败: {e}")
 
# 创建线程
def create_threads():
    """
    创建并启动下载线程。
    """
    chunk_size = file_size // num_threads
    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size - 1 if i != num_threads - 1 else file_size - 1
        queue.put((start, end))
 
    threads = []
    for _ in range(num_threads):
        start, end = queue.get()
        thread = Thread(target=download_chunk, args=(start, end))
        threads.append(thread)
        thread.start()
 
    for thread in threads:
        thread.join()
 
# 初始化文件
try:
    with open(filename, "wb") as f:
        f.write(b'\0' * file_size)
except IOError as e:
    print(f"初始化文件失败: {e}")
    exit(1)
 
# 显示下载进度
with tqdm(total=file_size, unit='B', unit_scale=True, desc=filename) as pbar:
    create_threads()
    pbar.update(file_size)
 
print("下载完成！")