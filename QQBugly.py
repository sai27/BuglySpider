# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import tea
else:
    import tea

import requests, re, os, tempfile, random, time, json
import base64, hashlib, rsa, binascii


class Bugly:
    appid       = 603049403
    urlConnect   = 'https://cas.bugly.qq.com/cas/login?service=https%3A%2F%2Fbugly.qq.com%2Fv2%2Fworkbench%2Fapps'
    urlLoginQQ  = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin'
    urlCheck    = 'https://ssl.ptlogin2.qq.com/check'
    urlLogin    = 'https://ssl.ptlogin2.qq.com/login'
    urlAppList  = 'https://bugly.qq.com/v2/users/null/appList'
    urlReferer	= 'https://cas.bugly.qq.com/cas/loginBack?type=9'
    urlSig      = ''
    
    headers = {
        'Upgrade-Insecure-Requests':'1',
        'Referer':'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?hide_border=1&hide_close_icon=1&low_login=0&appid=603049403&daid=276&s_url=https%3A%2F%2Fcas.bugly.qq.com%2Fcas%2FloginBack%3Ftype%3D9',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }
    def __init__(self, qq, pwd):
        self.qq          = qq
        self.pwd         = pwd
        self.nickname    = None
        self.vcode       = None
        self.session     = None
        self.vcodeShow   = 0
        self.loginSig    = None
        self.requests    = requests.Session()
        
        self.requests.get(self.urlConnect)
        
        par = {
            'hide_border'		: 1,
			'hide_close_icon'	: 1,
			'low_login'         : 0,
			'appid'             : self.appid,
            'daid'              : 276,
			's_url'             : self.urlReferer,
        }
        r = self.requests.get(self.urlLoginQQ, params=par, headers = self.headers)
        for x in r.cookies:
            if x.name == 'pt_login_sig':
                self.loginSig = x.value
                break
        self.check()

    def check(self):
        par = {
			'regmaster':'',
			'pt_tea':2,
			'pt_vcode':1,
			'uin':self.qq,
			'appid':self.appid,
			'js_ver':10199,
			'js_type':1,
			'login_sig':self.loginSig,
			'u1':self.urlReferer,
			'r':'0.6696087666316588',
			'pt_uistyle':40,
        }
        r = self.requests.get(self.urlCheck, params=par, headers = self.headers)
        
        li = re.findall('\'(.*?)\'', r.text)
        self.vcode = li[1]
        self.session = li[3]
        self.login()

    def getEncryption(self):
        puk = rsa.PublicKey(int(
            'F20CE00BAE5361F8FA3AE9CEFA495362'
            'FF7DA1BA628F64A347F0A8C012BF0B25'
            '4A30CD92ABFFE7A6EE0DC424CB6166F8'
            '819EFA5BCCB20EDFB4AD02E412CCF579'
            'B1CA711D55B8B0B3AEB60153D5E0693A'
            '2A86F3167D7847A0CB8B00004716A909'
            '5D9BADC977CBB804DBDCBA6029A97108'
            '69A453F27DFDDF83C016D928B3CBF4C7',
            16
        ), 3)
        e = int(self.qq).to_bytes(8, 'big')
        o = hashlib.md5(self.pwd.encode())
        r = bytes.fromhex(o.hexdigest())
        p = hashlib.md5(r + e).hexdigest()
        a = binascii.b2a_hex(rsa.encrypt(r, puk)).decode()
        s = hex(len(a) // 2)[2:]
        l = binascii.hexlify(self.vcode.upper().encode()).decode()
        c = hex(len(l) // 2)[2:]
        c = '0' * (4 - len(c)) + c
        s = '0' * (4 - len(s)) + s
        salt = s + a + binascii.hexlify(e).decode() + c + l
        return base64.b64encode(
            tea.encrypt(bytes.fromhex(salt), bytes.fromhex(p))
        ).decode().replace('/', '-').replace('+', '*').replace('=', '_')

    def login(self):
        d = self.requests.cookies.get_dict()
        if 'ptvfsession' in d:
            self.session = d['ptvfsession']

        par = {
            'p': self.getEncryption(),
			'u':self.qq,
			'verifycode':self.vcode,
			'pt_vcode_v1':self.vcodeShow,
			'pt_verifysession_v1':self.session,
			'pt_randsalt':0,
			'u1':self.urlReferer,
			'ptredirect':1,
			'h':1,
			't':1,
			'g':1,
			'from_ui':1,
			'ptlang':2052,
			'action':'17-20-1488361851213',
			'js_ver':10199,
			'js_type':1,
			'login_sig':self.loginSig,
			'pt_uistyle':40,
			'aid':self.appid,
			'daid':276,
        }
        r = self.requests.get(self.urlLogin, params=par, headers=self.headers)
        li = re.findall('https://[^\']+', r.text)
        if len(li):
            self.urlSig = li[0]
        
        self.check_sig()
    
    def check_sig(self):
        r = self.requests.get(self.urlSig, headers = self.headers)
        self.headers['x-token'] = str(self.get_xtoken())
        self.app_list()
        
    def app_list(self):
        par = {
			'userId':self.qq,
        }
        r = self.requests.get(self.urlAppList, params=par, headers=self.headers)
        self.appList = json.loads(r.text)['ret']
        #print(self.appList)
        
    def get_appId_by_pid(self, pid):
        for item in self.appList:
            if item['pid'] == pid:
                return item['appId']
        return ''
        
    def get_xtoken(self):         
        number = self.requests.cookies["token-skey"]
        t = 5381
        if (number):
          for i in number:
            t += (t << 5 & 2147483647) + i.encode('utf-8')[0]
          return 2147483647 & t
    
    def get_fsn(self):
        s = [ random.randint(0,255) for _ in range(0,16)]
        s[6] = 15 & s[6] | 64
        s[8] = 63 & s[8] | 128
        for i in range(len(s)):
            s[i] = "{0:#0{1}x}".format(s[i],4)[2:4]
        fsn = s[0]+s[1]+s[2]+s[3]+'-'+s[4]+s[5]+'-'+s[6]+s[7]+'-'+s[8]+s[9]+'-'+s[10]+s[11]+s[12]+s[13]+s[14]+s[15]
        return fsn
        
    def get(self, url, par = None):
        if par is None:
            par = {}
        par['fsn'] = self.get_fsn()
        r = self.requests.get(url, params = par, headers = self.headers)
        time.sleep(1)
        try:
            obj = json.loads(r.text)
            return obj
        except Exception as e:
            print(r.text)
		
if __name__ == '__main__':
    pass
