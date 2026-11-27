from solana_ai.tools.web import check_url

urls = [
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://localhost:11434",
    "http://169.254.169.254/latest/meta-data",
    "http://192.168.1.1",
    "http://[::1]/",
    "http://2130706433/",
    "file:///C:/Windows/win.ini",
    "ftp://example.com",
    "https://example.com",
]
for u in urls:
    print(u, "->", check_url(u))