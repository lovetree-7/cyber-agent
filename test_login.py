import urllib.request
import urllib.parse
import http.cookiejar
import re

print("==================================================")
print("🔬 正在启动 [DVWA 身份鉴权缺陷] 物理层专项测试程序...")
print("==================================================")

login_url = "http://localhost:8080/login.php"
username = "admin"
password = "password"

# 1. 初始化干净的 Cookie 罐子
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

# ---- 【核心刺探第一步】：执行第一次 GET，肉眼看清它吐出的源码 ----
try:
    print("\n[GET] 正在向登录页发起第一次握手刺探...")
    req_get = urllib.request.Request(login_url, headers={'User-Agent': 'DebugAgent/1.0'})
    with opener.open(req_get, timeout=5) as response:
        html_get = response.read().decode('utf-8', errors='ignore')
        
    print("✅ [GET 成功] 正在分析登录表单的底层特征...")
    
    # 提取并打印所有的 input 标签，看看里面到底埋了什么
    inputs = re.findall(r'<input[^>]*>', html_get, re.IGNORECASE)
    print("📌 发现的完整表单输入框组件列表:")
    for inp in inputs:
        print(f"  -> {inp}")
        
    # 测试常规提取算法
    token_match = re.search(r"name=['\"]user_token['\"].*?value=['\"](.*?)['\"]", html_get, re.IGNORECASE)
    user_token = token_match.group(1).strip() if token_match else None
    print(f"🎯 正则表达式当前提取到的 CSRF Token 为: [{user_token}]")

except Exception as e:
    print(f"❌ GET 刺探阶段暴毙，原因: {str(e)}")
    exit()

# ---- 【核心刺探第二步】：拼装表单并 POST，肉眼看清服务器的真实态度 ----
if not user_token:
    print("⚠️ 警告：未提取到 Token，将尝试空 Token 强投。")

form_data = {
    'username': username,
    'password': password,
    'Login': 'Login'
}
if user_token:
    form_data['user_token'] = user_token

encoded_data = urllib.parse.urlencode(form_data).encode('utf-8')

# 拼装带有 Referer 的高级请求头
post_req = urllib.request.Request(
    login_url,
    data=encoded_data,
    headers={
        'User-Agent': 'DebugAgent/1.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': login_url
    }
)

try:
    print("\n[POST] 正在向服务器投递管理员凭证组合...")
    with opener.open(post_req, timeout=5) as response:
        html_post = response.read().decode('utf-8', errors='ignore')
        final_url = response.geturl()
        post_headers = response.info()

    print("==================================================")
    print("📊 物理层响应数据核心审计报告")
    print("==================================================")
    print(f"1. 最终重定向落地 URL: {final_url}")
    
    print("2. 服务器返回的所有 Set-Cookie 响应头:")
    cookies = post_headers.get_all('Set-Cookie')
    if cookies:
        for c in cookies: print(f"  -> {c}")
    else:
        print("  -> [空] (极其危险！服务器竟然没有下发任何Cookie状态！)")

    print("\n3. 内存 CookieJar 最终固化的客户端通行证:")
    cookies_in_jar = [f"{c.name}={c.value} (Domain={c.domain})" for c in cookie_jar]
    if cookies_in_jar:
        for cj in cookies_in_jar: print(f"  -> {cj}")
    else:
        print("  -> [空] (CookieJar 拒绝保存或未匹配到有效域！)")

    print("\n4. 登录状态关键特征研判:")
    if "login failed" in html_post.lower():
        print("  🔥 [确诊特征]: 页面源码中依然包含 'Login failed' 字样！后端明确拒绝了这次会话。")
    elif "username" in html_post.lower() and "password" in html_post.lower():
        print("  🔥 [确诊特征]: 落地页依然包含了账号密码输入框！说明登录失败，被强行弹回了登录原点。")
    else:
        print("  🎉 [确诊特征]: 未发现登录失败特征，可能已成功越过登录墙！")
        
except Exception as e:
    print(f"❌ POST 投递阶段暴毙，严重系统级错误: {str(e)}")