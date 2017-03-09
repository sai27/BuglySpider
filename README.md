# QQBugly for python
---
对bugly平台中的错误分析进行本地拉取，方便后续进一步统一分析与处理项目产生的错误日志

依赖
---
第三方依赖库：[rsa](https://pypi.python.org/pypi/rsa/)、[requests](https://pypi.python.org/pypi/requests/)
``` sh
$ pip install rsa requests
```

参考
---
QQ登录部分参考了项目[qqlib](https://github.com/JetLua/qqlib)

使用
---
``` python
spider = QQBuglySpider.BuglySpider('qq','pwd', 'outpath', 'appId', 'pid', 'version')
spider_over = spider.run()
```