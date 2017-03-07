# -*- coding: utf-8 -*-

import QQBugly
def login():
    bugly=QQBugly.Bugly('qq','password')
    text = bugly.get('https://bugly.qq.com/v2/users/null/info')
    print(text)
    
login()
