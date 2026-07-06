import urllib.request
import json
import time
import re
import tools
import sys
import io
# ---- 【工业级编码矫正】：强行将 Windows 管道输出流锁死为 UTF-8，彻底粉碎 GBK 字符集死锁 ----
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SYSTEM_PROMPT = """你是一个具备内网穿透与身份鉴权破解能力的实战级渗透测试 Agent。
你必须通过逻辑严密的思考和精准的工具调用来评估目标主机的安全状态。

【严格的 ReAct 思考行为规范】：
每一轮思考，你必须且只能输出以下三个部分，不能带有任何多余的修饰文本：
Thought: 思考当前已获取的情报，分析目标可能存在的安全边界，决定下一步执行什么具体动作。
Action: 决定调用的工具名称（只能是 check_target_web、scan_target_ports、login_target_web 或 check_sql_injection）。
Action Input: 传入工具的纯文本参数值（直接写明字符串，严禁携带 {} 或 JSON 格式）。

【特别警示（收工判定）】：
当且仅当你认为所有开放端口都已摸排完毕，且高危服务的漏洞嗅探已有明确结果时，输出最终结论：
Final Answer: [包含资产列表、登录状态、高危漏洞位置及修复建议的完整渗透测试报告]

【你的高级工具箱（Action Space）】：
1. scan_target_ports: 扫描目标主机的常用安全测试端口（80, 443, 3306, 8080, 11434）。
2. check_target_web: 探测特定端口上的Web服务是否存活，并抓取网页指纹。
3. login_target_web: 自动化提交身份凭证组合（破除 CSRF 墙并固化 low 安全等级）。
   - 参数格式: 完整的登录URL, 用户名, 密码。例如: http://localhost:8080/login.php, admin, password
4. check_sql_injection: 针对指定的Web服务路径进行自动化 SQL 注入漏洞高危嗅探。
   - 参数: 目标的URL路径。例如: http://localhost:8080/vulnerabilities/sqli/
"""

def ask_local_llm(history_messages):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen2.5:14b",
        "messages": history_messages,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            return res_json['message']['content']
    except Exception as e:
        return f"通信失败: {str(e)}"

def run_agent(initial_task):
    print(f"\n🚀 [Agent 战力升级引擎启动] 初始任务: {initial_task}")
    
    memory = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": initial_task}
    ]
    
    max_steps = 6
    
    for step in range(1, max_steps + 1):
        print(f"\n======== 🔄 Agent 正在进行第 {step} 轮高级安全推理 ========")
        
        ai_response = ask_local_llm(memory)
        print(ai_response)
        
        memory.append({"role": "assistant", "content": ai_response})
        
        if "Final Answer:" in ai_response:
            final_report = ai_response.split("Final Answer:")[-1].strip()
            print("\n" + "="*50)
            print("🎉 【内网漏洞斩首战役完美通关！】最终渗透报告：")
            print("="*50)
            print(final_report)
            break
            
        action_match = re.search(r"Action:\s*(.*)", ai_response)
        action_input_match = re.search(r"Action Input:\s*(.*)", ai_response)
        
        if action_match and action_input_match:
            tool_name = action_match.group(1).strip()
            tool_arg = action_input_match.group(1).strip().strip('{}[]"\'')
            
            if "final" in tool_name.lower() or "answer" in tool_name.lower():
                print(f"\n🎉 【兜底机制触发】成功截获报告:\n{tool_arg}")
                break
            
            print(f"\n⚙️ [系统自动化执行]: 正在调度特种安全模块 [{tool_name}]")
            
            observation = ""
            if tool_name == "scan_target_ports":
                observation = tools.scan_target_ports(tool_arg)
            elif tool_name == "check_target_web":
                observation = tools.check_target_web(tool_arg)
            elif tool_name == "check_sql_injection":
                # ---- 【工业级容错】：如果大模型由于慌乱在 URL 后面拼接了 Cookie 等杂质参数 ----
                # 我们利用逗号切割，只取第一个干净的 URL 路径，彻底杜绝参数溢出导致的鉴权崩溃！
                clean_url = tool_arg.split(',')[0].strip()
                observation = tools.check_sql_injection(clean_url)
            elif tool_name == "login_target_web":
                try:
                    parts = [p.strip().strip('"\'') for p in tool_arg.split(',')]
                    if len(parts) >= 3:
                        observation = tools.login_target_web(parts[0], parts[1], parts[2])
                    else:
                        observation = "错误：login_target_web 工具需要 3 个参数（URL, 账号, 密码）。"
                except Exception as parse_err:
                    observation = f"参数解析发生本地错误: {str(parse_err)}"
            else:
                observation = f"错误：调用的安全测试工具 [{tool_name}] 未注册或权限不足。"
                
            print(f"⚙️ [真实网络世界反馈] (Observation): {observation}")
            memory.append({"role": "user", "content": f"Observation: {observation}"})
            
        else:
            print("\n⚠️ 警告：Agent 输出格式偏离 ReAct 规范，控制线紧急拦截挂起。")
            break
    else:
        print("\n⚠️ 提示：达到了最大步数限制，智能体已安全退出。")

if __name__ == "__main__":
    task = "全面审计本地主机 localhost 的资产。提示：如果遇到登录拦截，可以尝试使用默认安全凭证组合（用户名: admin，密码: password）调用登录工具进行破墙，随后必须对内网核心路径 /vulnerabilities/sqli/ 展开深度的 SQL 注入高危漏洞嗅探！"
    run_agent(task)