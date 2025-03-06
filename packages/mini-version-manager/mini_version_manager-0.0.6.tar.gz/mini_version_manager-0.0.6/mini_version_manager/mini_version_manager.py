__all__ = ['version_manager','show_version_history']

import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import re
import logging
from datetime import datetime

def setup_logging():
    """设置日志记录"""
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )
    return logging.getLogger()

logger = setup_logging()

def create_hidden_root():
    """创建并隐藏主窗口"""
    root = tk.Tk()
    root.withdraw()
    return root

def select_folder(title):
    """选择文件夹"""
    root = create_hidden_root()
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(title=title,parent=root)
    root.destroy()
    return folder if folder else None

def get_commit_message():
    """获取提交说明"""
    root = create_hidden_root()  
    # 创建带滚动条的大文本输入框
    dialog = tk.Toplevel()
    dialog.attributes('-topmost', True)
    dialog.title("提交说明")
    dialog.geometry("400x600")
    
    text_frame = tk.Frame(dialog)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 设置更大的字体
    font = ("Arial", 12)
    
    text_area = tk.Text(
        text_frame, 
        wrap=tk.WORD, 
        yscrollcommand=scrollbar.set,
        font=font
    )
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar.config(command=text_area.yview)
    
    # 创建按钮框架
    button_frame = tk.Frame(dialog)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def on_ok():
        nonlocal message
        message = text_area.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("警告", "提交说明不能为空")
            return
        dialog.destroy()
    
    def on_cancel():
        nonlocal message
        message = ""
        dialog.destroy()
    
    # 添加提交和取消按钮
    tk.Button(
        button_frame, 
        text="提交",
        command=on_ok,
        width=10,
        bg="#4CAF50",
        fg="white"
    ).pack(side=tk.RIGHT, padx=5)
    
    tk.Button(
        button_frame,
        text="取消",
        command=on_cancel,
        width=10
    ).pack(side=tk.RIGHT)
    
    message = ""
    
    dialog.wait_window()
    root.destroy()
    return message

def record_version_history(src, dest, message, timestamp):
    """记录版本历史"""
    try:
        log_file = os.path.join(dest, "version_history.md")
        folder_name = os.path.basename(src)
        username = os.getlogin()
        
        # 确保目标目录存在
        os.makedirs(dest, exist_ok=True)
        
        # 获取当前提交序号
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                commit_count = content.count("## ") + 1
        else:
            commit_count = 1
        
        # 获取重命名后的文件夹名
        version = get_version_number(dest)
        renamed_folder = f"{folder_name}_v{version}-{timestamp}"
        
        # 格式化提交信息
        log_entry = f"""
## {commit_count:03d} 提交信息

| 项目            | 内容                     |
|-----------------|--------------------------|
| 提交时间        | {timestamp}             |
| 提交人          | {username}              |
| 提交文件        | {folder_name}           |
| 重命名文件夹    | {renamed_folder}        |
| 提交说明        |                          |
{message}

---

"""
        
        # 如果文件不存在，先写入标题
        if not os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("# 文件夹版本历史记录\n\n")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        logger.info(f"成功写入日志文件：{log_file}")
    except Exception as e:
        logger.error(f"写入日志文件失败：{e}")

def get_version_number(dest):
    """获取当前版本号"""
    # 获取当前日期
    now = datetime.now()
    month = now.month
    day = now.day
    
    # 初始化变量
    content = ""
    count = 1
    
    # 从version_history.md获取当天提交次数
    history_file = os.path.join(dest, "version_history.md")
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"读取版本历史文件失败: {e}")
            return f"{month}_{day}_{count}"
    
    # 查找所有当天提交的文件夹名
    pattern = re.compile(rf"\| 重命名文件夹    \| .*_v{month}_{day}_(\d+)-{now.strftime('%Y%m%d')}_\d{{6}}")
    matches = pattern.findall(content)
    
    # 获取最大版本号
    if matches:
        version_numbers = [int(m) for m in matches]
        count = max(version_numbers) + 1
    
    return f"{month}_{day}_{count}"

def copy_and_rename_folder(src, dest, message):
    """复制并重命名文件夹"""
    if not src or not dest:
        return False
        
    # 获取当前时间
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 获取源文件夹名
    folder_name = os.path.basename(src)
    # 获取版本号
    version = get_version_number(dest)
    # 创建新文件夹名
    new_folder_name = f"{folder_name}_v{version}-{timestamp}"
    # 目标路径
    dest_path = os.path.join(dest, new_folder_name)
    
    try:
        # 初始化日志
        logger.info(f"开始提交文件夹: {src}")
        logger.info(f"目标路径: {dest_path}")
        
        shutil.copytree(src, dest_path)
        logger.info("文件夹复制成功")
        
        # 记录版本历史
        record_version_history(src, dest, message, timestamp)
        logger.info("版本历史记录成功")
        
        return True
    except Exception as e:
        logger.error(f"文件夹提交失败: {str(e)}")
        return False

def version_manager():
    # 选择源文件夹
    src_folder = select_folder("请选择要提交的文件夹")
    if not src_folder:
        messagebox.showerror("错误", "必须选择一个源文件夹")
        return
        
    # 获取提交说明
    commit_message = get_commit_message()
    if not commit_message:
        messagebox.showerror("错误", "必须输入提交说明")
        return
        
    # 选择目标文件夹
    dest_folder = select_folder("请选择存储位置")
    if not dest_folder:
        messagebox.showerror("错误", "必须选择一个目标文件夹")
        return
        
    # 执行复制操作
    if copy_and_rename_folder(src_folder, dest_folder, commit_message):
        messagebox.showinfo("成功", "文件夹已成功提交！")
    else:
        messagebox.showerror("错误", "文件夹提交失败")

def show_version_history():
    # 选择目标文件夹
    dest_folder = select_folder("请选择存储位置")
    if not dest_folder:
        messagebox.showerror("错误", "必须选择一个目标文件夹")
        return
        
    # 打开版本历史文件
    history_file = os.path.join(dest_folder, "version_history.md")
    if os.path.exists(history_file):
        os.startfile(history_file)
        logger.info(f"成功打开版本历史文件: {history_file}")
        return
    else:
        messagebox.showerror("错误", "版本历史文件不存在")
        return

if __name__ == '__main__':
    
    version_manager()
    # show_version_history()