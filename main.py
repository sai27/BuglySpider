# -*- coding: utf-8 -*-

import time
import QQBuglySpider

def execute_spider():
    spider_over = False
    while(spider_over == False):
        spider = QQBuglySpider.BuglySpider('qq','pwd', 'D:/bugly_content/', 'appId', 'pid')
        spider_over = spider.run()
        del spider
        # 如果发生异常，等待10分钟重连
        if spider_over == False:
            print('爬虫发生异常返回,10分钟后重连')
            time.sleep(600)

execute_spider()
