```
Written by HelloWorld05
20250404
```
import tkinter as tk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
import requests

class DownloaderApp:
    """下载器主应用程序类."""
    def __init__(self, root):
        """初始化下载器界面并设置组件."""
        self.root = root
        self.root.title("多线程下载器")
        self.root.geometry("400x200")

        self.url_label = tk.Label(root, text="下载链接:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.threads_label = tk.Label(root, text="线程数:")
        self.threads_label.pack(pady=5)

        self.threads_entry = tk.Entry(root, width=10)
        self.threads_entry.pack(pady=5)
        self.threads_entry.insert(0, "4")

        self.save_button = tk.Button(root, text="选择保存位置", command=self.select_save_path)
        self.save_button.pack(pady=5)

        self.save_path_var = tk.StringVar()
        self.save_path_label = tk.Label(root, textvariable=self.save_path_var)
        self.save_path_label.pack(pady=5)

        self.download_button = tk.Button(root, text="开始下载", command=self.start_download)
        self.download_button.pack(pady=20)

        self.save_path = None
        self.executor = None

    def show_error(self, title, message):
        """显示错误提示."""
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """显示信息提示."""
        messagebox.showinfo(title, message)

    def select_save_path(self):
        """选择文件保存路径."""
        self.save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All Files", "*.*")])
        if self.save_path:
            self.save_path_var.set(f"保存路径: {self.save_path}")
        else:
            self.show_error("选择错误", "未选择保存位置。")

    def download_chunk(self, url, start, end, file_stream):
        """下载指定范围的文件块."""
        try:
            headers = {'Range': f'bytes={start}-{end}'}
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024):
                file_stream.write(chunk)
        except Exception as e:
            self.show_error("下载错误", f"下载失败: {e}")

    def multi_thread_download(self, url, num_threads, save_path):
        """使用多线程下载文件."""
        try:
            response = requests.head(url, allow_redirects=True)
            content_length = int(response.headers.get('content-length', 0))
            if content_length == 0:
                raise ValueError("无法获取文件大小")

            if num_threads > content_length // 1024:
                num_threads = content_length // 1024 or 1
                self.show_info("提示", f"线程数大于文件大小，已自动调整为 {num_threads} 个线程。")

            chunk_size = content_length // num_threads
            with open(save_path, 'wb') as f:
                threads = []
                for i in range(num_threads):
                    start = i * chunk_size
                    end = start + chunk_size - 1 if i != num_threads - 1 else content_length - 1
                    stream = open(save_path + f'.part{i}', 'wb')  # 直接写入文件，避免使用额外的内存流
                    thread = self.executor.submit(self.download_chunk, url, start, end, stream)
                    threads.append((thread, stream))

                for thread, stream in threads:
                    thread.result()
                    stream.close()

            # 合并所有部分文件
            with open(save_path, 'wb') as f:
                for i in range(num_threads):
                    with open(save_path + f'.part{i}', 'rb') as part_file:
                        f.write(part_file.read())
                    part_file.close()
                    import os
                    os.remove(save_path + f'.part{i}')  # 删除部分文件

            self.show_info("下载完成", f"{save_path} 下载完成!")
        except Exception as e:
            self.show_error("下载错误", f"下载失败: {e}")

    def start_download(self):
        """启动文件下载过程."""
        url = self.url_entry.get()
        try:
            num_threads = int(self.threads_entry.get())
        except ValueError:
            self.show_error("输入错误", "线程数必须是数字")
            return

        if not url or not self.save_path or num_threads <= 0:
            self.show_error("输入错误", "请检查所有输入字段")
            return

        self.executor = ThreadPoolExecutor(max_workers=num_threads)
        self.multi_thread_download(url, num_threads, self.save_path)
        self.executor.shutdown()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
