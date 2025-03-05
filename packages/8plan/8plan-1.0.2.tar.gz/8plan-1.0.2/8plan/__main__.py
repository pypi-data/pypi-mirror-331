import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import datetime
import os

class FOVBPSKRunnerApp:
    def __init__(self, master):
        self.master = master
        master.title("8PLAN 控制台")
        master.geometry("900x680")

        # 初始化样式系统
        self.init_styles()

        # 创建标签页容器
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # 创建功能标签页
        self.create_send_tab()
        self.create_receive_tab()
        self.create_debug_tab()


        # 初始化运行状态
        self.log_file = "all_log.txt"
        self.custom_env = {}
        self.process = None
        self.is_running = False

        # 创建输出控制台
        self.create_output_console()

    def init_styles(self):
        """初始化界面样式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 配置全局样式
        self.style.configure('.', font=('微软雅黑', 9))
        self.style.configure('TNotebook.Tab',
                           font=('微软雅黑', 10, 'bold'),
                           padding=[15,5])
        self.style.configure('Title.TLabel',
                           font=('微软雅黑', 11, 'bold'),
                           foreground='#2c3e50')

        # 特殊按钮样式
        self.style.configure('Accent.TButton',
                           background='#4CAF50',
                           foreground='white',
                           borderwidth=0)
        self.style.map('Accent.TButton',
                     background=[('active', '#45a049'), ('!disabled', '#4CAF50')],
                     foreground=[('active', 'white')])

        # 错误标签样式
        self.style.configure('Error.TEntry',
                           foreground='red',
                           fieldbackground='#ffeeee')

    def create_output_console(self):
        """创建底部输出控制台"""
        console_frame = ttk.Frame(self.master)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # 工具栏
        toolbar = ttk.Frame(console_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="清空日志", command=self.clear_log).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="导出日志", command=self.export_log).pack(side=tk.RIGHT, padx=5)

        # 文本区域
        self.output_text = tk.Text(console_frame,
                                 wrap=tk.WORD,
                                 font=('Consolas', 9),
                                 padx=10,
                                 pady=10,
                                 undo=True)
        scrollbar = ttk.Scrollbar(console_frame, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # 标签配置
        self.output_text.tag_config('ERROR', foreground='#e74c3c')
        self.output_text.tag_config('SUCCESS', foreground='#2ecc71')
        self.output_text.tag_config('WARNING', foreground='#f1c40f')

        # 布局
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_debug_tab(self):
        """调试标签页"""
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text='调试')

        # 环境变量设置
        env_group = ttk.LabelFrame(debug_frame, text="环境变量设置", padding=(15,10))
        env_group.pack(fill=tk.BOTH, padx=15, pady=10)

        ttk.Label(env_group, text="每行一个 KEY=VALUE:").pack(anchor=tk.W)
        self.env_text = tk.Text(env_group, height=5, width=60, padx=5, pady=5)
        self.env_text.pack(fill=tk.X, pady=3)
        self.env_text.insert(tk.END, "# 示例\nBITRATE=1\n#SAMPLERATE=8000")
        self.env_text.bind("<KeyRelease>", self.validate_env_input)

        # 参数输入区
        input_group = ttk.Frame(debug_frame)
        input_group.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(input_group, text="运行参数:").pack(side=tk.LEFT)
        self.args_entry = ttk.Entry(input_group, width=60)
        self.args_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # 输入验证
        validate_cmd = (self.master.register(self.validate_args), '%P')
        self.args_entry.configure(
            validate="key",
            validatecommand=validate_cmd
        )

        # 控制按钮
        self.run_btn = ttk.Button(input_group,
                                text="▶ 启动",
                                command=self.toggle_run,
                                style='Accent.TButton')
        self.run_btn.pack(side=tk.RIGHT)

    def create_send_tab(self):
        """发送标签页"""
        send_frame = ttk.Frame(self.notebook)
        self.notebook.add(send_frame, text='发送')

        config_group = ttk.LabelFrame(send_frame, text="发送配置", padding=(15,10))
        config_group.pack(fill=tk.BOTH, padx=15, pady=10)

        # QAM设置
        qam_row = ttk.Frame(config_group)
        qam_row.pack(fill=tk.X, pady=5)
        ttk.Label(qam_row, text="QAM调制:").pack(side=tk.LEFT)
        self.send_qam = ttk.Combobox(qam_row, values=["关闭", "2", "4"], state="readonly", width=6)
        self.send_qam.current(0)
        self.send_qam.pack(side=tk.LEFT, padx=10)
        self.send_qam.bind("<<ComboboxSelected>>", lambda e: self.calculate_send_time())

        # 文件选择
        file_row = ttk.Frame(config_group)
        file_row.pack(fill=tk.X, pady=5)
        ttk.Button(file_row, text="📁 选择文件", command=self.select_send_file).pack(side=tk.LEFT)
        self.send_file_info = ttk.Label(file_row, text="未选择文件", foreground="#666666")
        self.send_file_info.pack(side=tk.LEFT, padx=10)

        # 选项组
        opt_row = ttk.Frame(config_group)
        opt_row.pack(fill=tk.X, pady=5)
        self.send_verbose = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_row, text="详细输出", variable=self.send_verbose).pack(side=tk.LEFT, padx=10)
        self.send_compress = tk.BooleanVar()
        ttk.Checkbutton(opt_row, text="压缩传输", variable=self.send_compress).pack(side=tk.LEFT, padx=10)

        # 预计时间
        time_row = ttk.Frame(config_group)
        time_row.pack(fill=tk.X, pady=5)
        self.send_time_label = ttk.Label(time_row, text="预计发送时间：0秒", foreground="#009900")
        self.send_time_label.pack(side=tk.LEFT)

        # 操作按钮
        btn_frame = ttk.Frame(send_frame)
        btn_frame.pack(pady=15)
        self.send_start_btn = ttk.Button(btn_frame,
                 text="🚀 开始发送",
                 command=self.start_send,
                 style='Accent.TButton')
        self.send_start_btn.pack(padx=20, ipadx=20)

    def create_receive_tab(self):
        """接收标签页"""
        receive_frame = ttk.Frame(self.notebook)
        self.notebook.add(receive_frame, text='接收')

        config_group = ttk.LabelFrame(receive_frame, text="接收配置", padding=(15,10))
        config_group.pack(fill=tk.BOTH, padx=15, pady=10)

        # QAM设置
        qam_row = ttk.Frame(config_group)
        qam_row.pack(fill=tk.X, pady=5)
        ttk.Label(qam_row, text="QAM调制:").pack(side=tk.LEFT)
        self.recv_qam = ttk.Combobox(qam_row, values=["关闭", "2", "4"], state="readonly", width=6)
        self.recv_qam.current(0)
        self.recv_qam.pack(side=tk.LEFT, padx=10)

        # 选项组
        opt_row = ttk.Frame(config_group)
        opt_row.pack(fill=tk.X, pady=5)
        self.recv_verbose = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_row, text="详细输出", variable=self.recv_verbose).pack(side=tk.LEFT, padx=10)
        self.recv_compress = tk.BooleanVar()
        ttk.Checkbutton(opt_row, text="解压文件", variable=self.recv_compress).pack(side=tk.LEFT, padx=10)

        # 保存路径
        path_row = ttk.Frame(config_group)
        path_row.pack(fill=tk.X, pady=5)
        ttk.Button(path_row, text="📂 选择路径", command=self.select_save_path).pack(side=tk.LEFT)
        self.save_path_info = ttk.Label(path_row, text="默认路径: received_files", foreground="#666666")
        self.save_path_info.pack(side=tk.LEFT, padx=10)

        # 操作按钮
        btn_frame = ttk.Frame(receive_frame)
        btn_frame.pack(pady=15)
        self.receive_start_btn = ttk.Button(btn_frame,
                 text="📥 开始接收",
                 command=self.start_receive,
                 style='Accent.TButton')
        self.receive_start_btn.pack(padx=20, ipadx=20)

    # 以下是功能方法实现（与之前版本相似但包含改进）
    def select_save_path(self):
        """选择接收文件保存路径"""
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.save_path_info.config(text=f"保存到: {path}", foreground="#000000")

    def validate_args(self, text):
        """验证参数输入"""
        if any(c in text for c in ";&|<>"):
            self.args_entry.config(style='Error.TEntry')
            return False
        self.args_entry.config(style='TEntry')
        return True

    def select_send_file(self):
        self.send_file_path = filedialog.askopenfilename()
        if self.send_file_path:
            size = os.path.getsize(self.send_file_path)
            human_size = self.format_size(size)
            self.send_file_info.config(text=f" {os.path.basename(self.send_file_path)} ({human_size})",
                                     foreground="#000000")
            self.calculate_send_time()

    def format_size(self, size):
        """将字节数转换为易读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def calculate_send_time(self):
        if hasattr(self, 'send_file_path') and self.send_file_path:
            bitrate_map = {"关闭":1, "2":2, "4":4}
            bitrate = bitrate_map[self.send_qam.get()]
            file_bits = os.path.getsize(self.send_file_path) * 8
            seconds = file_bits / (bitrate * 1000)

            if seconds > 3600:
                time_str = f"{seconds/3600:.1f} 小时"
            elif seconds > 60:
                time_str = f"{seconds/60:.1f} 分钟"
            else:
                time_str = f"{seconds:.1f} 秒"

            self.send_time_label.config(text=f"预计发送时间：{time_str}")

    def start_send(self):
        if not hasattr(self, 'send_file_path'):
            messagebox.showwarning("提示", "请先选择要发送的文件")
            return

        # 显示进度条
        self.show_progress("正在发送数据...")
        self.send_start_btn.config(text="⏹ 停止发送", command=self.stop_script)

        self.custom_env["BITRATE"] = "1" if self.send_qam.get() == "关闭" else self.send_qam.get()
        args = ["send"]
        args += ["-i", self.send_file_path]
        if self.send_verbose.get(): args.append("-vv")
        if self.send_compress.get(): args.append("-z")
        self.run_script(args)

    def start_receive(self):
        # 显示进度条
        self.show_progress("正在等待接收数据...")
        self.receive_start_btn.config(text="⏹ 停止接收", command=self.stop_script)

        self.custom_env["BITRATE"] = "1" if self.recv_qam.get() == "关闭" else self.recv_qam.get()
        args = ["recv"]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = getattr(self, 'save_path', 'received_files')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{timestamp}.bin")
        args += ["-o", output_path]
        if self.recv_verbose.get(): args.append("-vv")
        if self.recv_compress.get(): args.append("-z")
        self.run_script(args)

    def show_progress(self, message):
        """显示进度条"""
        self.progress = ttk.Progressbar(self.master,
                                      mode='indeterminate',
                                      length=280)
        self.progress.pack(pady=10)
        self.progress.start(10)
        self.status_label = ttk.Label(self.master,
                                    text=message,
                                    foreground="#2c3e50")
        self.status_label.pack()

    def hide_progress(self):
        """隐藏进度条"""
        if hasattr(self, 'progress'):
            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.pack_forget()

    def validate_env_input(self, event=None):
        content = self.env_text.get("1.0", tk.END)
        for i, line in enumerate(content.split('\n')):
            line = line.strip()
            if line and not line.startswith('#') and '=' not in line:
                self.env_text.tag_add("error", f"{i+1}.0", f"{i+1}.end")
                self.env_text.tag_config("error", foreground="red")
            else:
                self.env_text.tag_remove("error", f"{i+1}.0", f"{i+1}.end")

    def parse_env_vars(self):
        self.custom_env.clear()
        content = self.env_text.get("1.0", tk.END).strip()
        for line in content.split('\n'):
            line = line.split('#')[0].strip()
            if line and '=' in line:
                key, value = line.split('=', 1)
                self.custom_env[key.strip()] = value.strip()

    def toggle_run(self):
        if self.is_running:
            self.stop_script()
        else:
            self.parse_env_vars()
            args = self.args_entry.get().split()
            if args:
                self.run_script(args)
            else:
                messagebox.showwarning("提示", "请输入运行参数")

    def run_script(self, extra_args):
        cmd = ["python", "-m", "fovbpsk"] + extra_args
        try:
            env = os.environ.copy()
            env.update(self.custom_env)

            self._write_log(f"执行命令: {' '.join(cmd)}")
            self._write_log(f"环境变量: {self.custom_env}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
                bufsize=1
            )
            self.is_running = True
            self.run_btn.config(text="⏹ 停止")
            threading.Thread(target=self.monitor_output, daemon=True).start()
        except Exception as e:
            self.output_text.insert(tk.END, f"启动失败 QwQ: {str(e)}\n", 'ERROR')
            self.hide_progress()

    def stop_script(self):
        if self.process:
            try:
                self.process.terminate()
                # 等待一段时间，如果进程没有结束，则强制终止
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.is_running = False
        self.run_btn.config(text="▶ 启动")
        if hasattr(self, 'send_start_btn'):
            self.send_start_btn.config(text="🚀 开始发送", command=self.start_send)
        if hasattr(self, 'receive_start_btn'):
            self.receive_start_btn.config(text="📥 开始接收", command=self.start_receive)
        self.output_text.insert(tk.END, "操作已停止\n", 'SUCCESS')
        self.hide_progress()

    def monitor_output(self):
        while self.is_running and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                # 自动染色输出
                tag = None
                line_lower = line.lower()
                if 'error' in line_lower:
                    tag = 'ERROR'
                elif 'success' in line_lower:
                    tag = 'SUCCESS'
                elif 'warning' in line_lower:
                    tag = 'WARNING'

                self.output_text.insert(tk.END, line, tag)
                self.output_text.see(tk.END)
                self._write_log(line.strip())
                self.master.update_idletasks()

        # 进程结束后处理
        self.stop_script()

    def _write_log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def clear_log(self):
        """清空日志窗口"""
        self.output_text.delete(1.0, tk.END)

    def export_log(self):
        """导出日志文件"""
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("所有文件", "*.*")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.output_text.get(1.0, tk.END))
                messagebox.showinfo("导出成功", f"日志已保存到：\n{path}")
            except Exception as e:
                messagebox.showerror("导出失败", f"保存失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FOVBPSKRunnerApp(root)
    root.mainloop()
