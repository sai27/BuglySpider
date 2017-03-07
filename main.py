# -*- coding: utf-8 -*-

import QQBugly
import json, time, os

def save_cfg(cfg):
    with open('cfg.json','w') as f:
        f.write(json.dumps(cfg))

def load_cfg():
    cfg = {
        's1_page':0,
        's1_idx':0,
        's2_page':0,
        's2_idx':0,
        }

    if os.path.isfile('cfg.json') == True:
        with open('cfg.json', 'r') as f:
            text = f.read()
            cfg = json.loads(text)
    return cfg

def catched(status, cfg):
    if status!=200:
        print('is catched by anti-spider:', status)
        save_cfg(cfg)
        return True
    return False

def step1(bugly, cfg, appId, pid):
    obj = bugly.get('https://bugly.qq.com/v2/issueList', {
        'start':0,
        'searchType':'errorType',
        'pid':pid,
        'exceptionTypeList':'AllCatched,Unity3D,Lua,JS',
        'sortOrder':'desc',
        'sortField':'crashCount',
        'appId':appId,
        'platformId':'1',
        'rows':'10',
        })
    
    if catched(obj['status'], cfg):
        return

    pages = obj['ret']['numFound']
    while cfg['s1_page'] < pages:
        obj = bugly.get('https://bugly.qq.com/v2/issueList', {
            'start':str(cfg['s1_page']),
            'searchType':'errorType',
            'pid':pid,
            'exceptionTypeList':'AllCatched,Unity3D,Lua,JS',
            'sortOrder':'desc',
            'sortField':'crashCount',
            'appId':appId,
            'platformId':'1',
            'rows':'50',
            })
    
        if catched(obj['status'], cfg):
            return False

        issueList = obj['ret']['issueList']
        while cfg['s1_idx'] < len(issueList):
            issueId = issueList[cfg['s1_idx']]['issueId']
            if (step2(bugly,cfg,issueId, appId, pid)== False):
                return False
            cfg['s1_idx']+=1
        cfg['s1_page'] += 50
    return True
            
def step2(bugly, cfg, issueId, appId, pid):
    obj = bugly.get('https://bugly.qq.com/v2/crashList', {
        'start':str(cfg['s2_page']),
        'searchType':'detail',
        'pid':pid,
        'exceptionTypeList':'AllCatched,Unity3D,Lua,JS',
        'sortOrder':'desc',
        'sortField':'crashCount',
        'appId':appId,
        'platformId':1,
        'rows':'10',
        'issueId':issueId,
        })
    
    if catched(obj['status'], cfg):
        return

    pages = obj['ret']['numFound']
    while cfg['s2_page'] < pages:
        obj = bugly.get('https://bugly.qq.com/v2/crashList', {
            'start':str(cfg['s2_page']),
            'searchType':'detail',
            'pid':pid,
            'exceptionTypeList':'AllCatched,Unity3D,Lua,JS',
            'sortOrder':'desc',
            'sortField':'crashCount',
            'appId':appId,
            'platformId':1,
            'rows':'50',
            'issueId':issueId,
            })
    
        if catched(obj['status'], cfg):
            return False

        #print(obj)
        crashIdList = obj['ret']['crashIdList']
        while cfg['s2_idx'] < len(crashIdList):
            crashId = crashIdList[cfg['s2_idx']]
            if (step3(bugly,cfg,crashId, appId, pid)== False):
                return False
            cfg['s2_idx'] += 1
        cfg['s2_page'] += 50
    return True

def step3(bugly, cfg, crashId, appId, pid):
    crashDocUrl = 'https://bugly.qq.com/v2/crashDoc/appId/'+appId+'/platformId/'+str(pid)+'/crashHash/'+crashId
    crashDoc = bugly.get(crashDocUrl)
    if catched(crashDoc['status'], cfg):
        return False

    name = str(crashDoc['ret']['crashMap']['crashId'])
    appDetailCrashUrl = 'https://bugly.qq.com/v2/appDetailCrash/appId/'+appId+'/platformId/'+str(pid)+'/crashHash/'+crashId
    appDetailCrash = bugly.get(appDetailCrashUrl)
    if catched(appDetailCrash['status'], cfg):
        return False

    with open(name+'_crashDoc.json','w') as f:
        f.write(json.dumps(crashDoc['ret']))

    with open(name+'_appDetail.json','w') as f:
        f.write(json.dumps(appDetailCrash['ret']))

    print(name, 'OK')
    return True

def start_spider():
    dir_path = 'D:/bugly_content/'
    if os.path.exists(dir_path) == False:
        os.mkdir(dir_path)
    os.chdir(dir_path)
    
    cfg = load_cfg()

    # 初始化与bugly的连接
    bugly=QQBugly.Bugly('qq','pwd')

    pid = 1
    appId = bugly.get_appId_by_pid(pid)
    step1(bugly,cfg, appId, pid)
    
start_spider()
