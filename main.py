import os
import re
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from tkinter import ttk

def extract_first_number(filename):
    """
    从文件名中提取第一个数字，如果没有数字，则返回一个较大的默认值。
    """
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def extract_date(filename):
    """
    从文件名中提取日期 (格式: YYYY-MM-DD 或 YYYY-M-D)，如果没有找到日期，则返回较大的默认值。
    """
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return "9999-12-31"

def get_file_order_with_ui(files):
    """
    弹出一个UI窗口，允许用户调整文件顺序。
    """
    def move_up():
        selected = listbox.curselection()
        if not selected:
            return
        for index in selected:
            if index == 0:
                continue
            files[index - 1], files[index] = files[index], files[index - 1]
            listbox.delete(index)
            listbox.insert(index - 1, files[index - 1])
            listbox.selection_set(index - 1)

    def move_down():
        selected = listbox.curselection()
        if not selected:
            return
        for index in reversed(selected):
            if index == len(files) - 1:
                continue
            files[index + 1], files[index] = files[index], files[index + 1]
            listbox.delete(index)
            listbox.insert(index + 1, files[index + 1])
            listbox.selection_set(index + 1)

    def confirm():
        root.destroy()

    root = tk.Tk()
    root.title("调整文件顺序")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=15)
    listbox.pack(side=tk.LEFT, padx=5)

    for file in files:
        listbox.insert(tk.END, file)

    button_frame = tk.Frame(frame)
    button_frame.pack(side=tk.LEFT, padx=5)

    up_button = tk.Button(button_frame, text="上移", command=move_up)
    up_button.pack(pady=5)

    down_button = tk.Button(button_frame, text="下移", command=move_down)
    down_button.pack(pady=5)

    confirm_button = tk.Button(root, text="确定", command=confirm)
    confirm_button.pack(pady=10)

    root.mainloop()
    return files

def concatenate_md_files_with_ui(directory):
    output_file = "note.md"
    md_files = [
        f for f in os.listdir(directory)
        if f.endswith(".md") and f != output_file
    ]

    # 弹出选择排序方式的对话框
    def ask_sorting_method():
        method = simpledialog.askinteger(
            "选择排序方式",
            "1: 按字典序排序\n2: 按日期排序 (YYYY-MM-DD)\n3: 按第一个数字大小排序\n请输入对应数字:",
            minvalue=1,
            maxvalue=3
        )
        return method

    sorting_method = ask_sorting_method()
    if sorting_method == 1:
        md_files.sort()
    elif sorting_method == 2:
        md_files.sort(key=extract_date)
    elif sorting_method == 3:
        md_files.sort(key=extract_first_number)
    else:
        messagebox.showinfo("提示", "未选择有效的排序方式，默认按字典序排序。")
        md_files.sort()


    # 弹出UI调整顺序
    final_order = get_file_order_with_ui(md_files)

    output_path = os.path.join(directory, output_file)

    header_written = False
    header_content = ""

    with open(output_path, "w", encoding="utf-8") as outfile:
        for i, md_file in enumerate(final_order):
            file_path = os.path.join(directory, md_file)
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read()
                if i == 0:  # 仅处理第一个文件的头部配置
                    header_match = re.match(r'---\n(.*?)\n---', content, re.S)
                    if header_match:
                        header_content = header_match.group(0) + "\n"
                    # 移除第一个文件的头部配置
                    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.S)
                else:
                    # 移除其他文件的头部配置和 @import 开头的行
                    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.S)
                    content = re.sub(r'^@import.*$', '', content, flags=re.M)
                outfile.write(content)
                ### outfile.write("\n___\n")  # 添加换行分隔符

        # 在输出文件的开头写入第一个文件的头部配置
        if header_content:
            with open(output_path, "r+", encoding="utf-8") as final_outfile:
                original_content = final_outfile.read()
                final_outfile.seek(0, 0)
                final_outfile.write(header_content + original_content)

    print(f"All .md files have been concatenated into {output_file}.")


# 示例调用
directory_path = filedialog.askdirectory(title="选择目标目录")
if directory_path:
    concatenate_md_files_with_ui(directory_path)
else:
    messagebox.showinfo("提示", "未选择任何目录。")
