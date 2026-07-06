import sys
import tkinter as tk
from tkinter import scrolledtext
import threading
import subprocess
import os
import sys
import io
# ---- 【工业级编码矫正】：强行将 Windows 管道输出流锁死为 UTF-8，彻底粉碎 GBK 字符集死锁 ----
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SecurityAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CyberAgent 智能电脑资产安全体检卫士")
        self.root.geometry("750x500")
        self.root.configure(bg="#2c3e50")
        
        # 顶部大标题
        self.title_label = tk.Label(
            root, text="🛡️ CyberAgent 自动化安全审计系统", 
            font=("Microsoft YaHei", 14, "bold"), fg="#ecf0f1", bg="#2c3e50"
        )
        self.title_label.pack(pady=10)
        
        # 日志显示区域（全量穿透流）
        self.log_area = scrolledtext.ScrolledText(
            root, width=90, height=18, 
            font=("Consolas", 10), fg="#2ecc71", bg="#1a252f",
            insertbackground="white"
        )
        self.log_area.pack(pady=10)
        self.log_area.insert(tk.END, "💡 系统就绪。点击下方【开始一键资产体检】启动 AI 审计...\n")
        self.log_area.configure(state='disabled')
        
        # 底部状态栏
        self.status_label = tk.Label(
            root, text="当前状态: 准备就绪", 
            font=("Microsoft YaHei", 10), fg="#bdc3c7", bg="#2c3e50"
        )
        self.status_label.pack(pady=5)
        
        # 控制按钮
        self.start_btn = tk.Button(
            root, text="🚀 开始一键资产体检", 
            font=("Microsoft YaHei", 11, "bold"), fg="white", bg="#2980b9",
            activebackground="#3498db", activeforeground="white",
            command=self.start_audit_thread
        )
        self.start_btn.pack(pady=10)

    def write_log(self, text):
        """全量日志实时同步到文本区"""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, text)
        self.log_area.see(tk.END) # 强行将滚动条拉至最底层，确保用户始终看到最新进展
        self.log_area.configure(state='disabled')

    def start_audit_thread(self):
        """开启异步线程，防止后台推理大模型时导致前台界面无响应"""
        self.start_btn.configure(state='disabled', bg="#7f8c8d", text="🔄 正在审计中...")
        self.status_label.configure(text="当前状态: AI 正在进行多轮安全推理，请稍候...", fg="#f1c40f")
        
        audit_thread = threading.Thread(target=self.run_backend_agent)
        audit_thread.daemon = True
        audit_thread.start()

    def run_backend_agent(self):
        """全量实时同步后台核心引擎的终端字节流"""
        try:
            # 剥离系统缓存，强制推行逐字实时挤牙膏数据流
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            # 焊死工作区，彻底避免快捷方式引发的相对路径迷路
            project_dir = r"D:\cyber_agent"
            core_script = os.path.join(project_dir, "agent_core.py")

            process = subprocess.Popen(
                ["D:\\python\\python.exe", core_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                cwd=project_dir
            )
            
            has_high_risk = False
            self.write_log("\n🚀 [系统提示]: 成功唤醒核心安全智能体，全量实时日志开始同步...\n")
            
            # 不漏掉任何一行输出，百分之百还原大模型的长程思考
            for line in process.stdout:
                self.write_log(line)
                
                # 动态捕捉高危漏洞爆发的证据
                if "重磅高危漏洞预警" in line or "触发 sql 注入" in line.lower():
                    has_high_risk = True
            
            process.wait()
            
            # ---- 打印大结局体检报告 ----
            self.write_log("\n" + "="*50 + "\n")
            if has_high_risk:
                self.write_log("❌ 【最终体检报告】: 您的电脑处于 [ 高危 ] 状态！\n")
                self.write_log("💥 确诊原因: 本地开放的 8080 端口 Web 资产已被 AI 智能体强行穿透鉴权墙，并成功触发标准的 SQL 注入高危破坏特征，数据库存在沦陷风险！\n")
                self.status_label.configure(text="检测完毕: 您的系统处于高危状态，发现严重漏洞！", fg="#e74c3c")
            else:
                self.write_log("✅ 【最终体检报告】: 您的电脑当前 [ 安全 ]。\n")
                self.write_log("📌 确诊原因: AI 巡检完毕，未探测到可以被直接越权或穿透的敏感内网高危资产风险。\n")
                self.status_label.configure(text="检测完毕: 您的系统当前很安全。", fg="#2ecc71")
                
        except Exception as e:
            self.write_log(f"\n❌ 图形数据控制流发生异常: {str(e)}\n")
        finally:
            self.start_btn.configure(state='normal', bg="#2980b9", text="🚀 开始一键资产体检")

if __name__ == "__main__":
    app_root = tk.Tk()
    gui = SecurityAgentGUI(app_root)
    app_root.mainloop()