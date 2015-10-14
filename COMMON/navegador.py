# Navegador web

import sys
import os
import re
import http.client
import http.cookiejar
import http.cookies
import urllib.parse
import subprocess
import shlex
import io
import time
import six
import jsbeautifier
import gzip


def wc_L(s_File):
    shell_CMD_1 = ''.join(('more ',s_File))
    shell_CMD_2 = ''.join(('wc -l'))
    p1 = subprocess.Popen(shlex.split(shell_CMD_1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(shell_CMD_2), stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.wait()
    p2.wait()
    shell_Results = p2.communicate()[0]
    return(int(shell_Results.decode().strip('\n')))

def pipe_Shell_CMD(shell_CMDs):
    len = shell_CMDs.__len__()
    p = {}
    p[1] = subprocess.Popen(shlex.split(shell_CMDs[1]), stdout=subprocess.PIPE)
    for i in range(2,len):
        p[i] = subprocess.Popen(shlex.split(shell_CMDs[i]), stdin=p[i-1].stdout, stdout=subprocess.PIPE)
    p[len] = subprocess.Popen(shlex.split(shell_CMDs[len]), stdin=p[len-1].stdout, stdout=subprocess.PIPE)
    result = p[len].communicate()
    for i in range(2,len+1):
        p[i].wait()
    return(result)

class solicitud:
    def parse_Url(self,url):
        url_Scheme = urllib.parse.urlparse(url).scheme
        url_Netloc = urllib.parse.urlparse(url).netloc
        url_Path = urllib.parse.urlparse(url).path
        url_Params = urllib.parse.urlparse(url).params
        url_Query = urllib.parse.urlparse(url).query
        url_Fragment = urllib.parse.urlparse(url).fragment
        return((url_Scheme,url_Netloc,url_Path,url_Params,url_Query,url_Fragment))
    def parse_Url_Netloc(self,url_Netloc,default_Port):
        regex_Netloc = re.compile('(.*):(.*)')
        m = regex_Netloc.search(url_Netloc)
        if(m == None):
            url_Netloc_Host = url_Netloc
            url_Netloc_Port = default_Port
        else:
            url_Netloc_Host = m.group(1)
            url_Netloc_Port = m.group(2)
        return((url_Netloc_Host,url_Netloc_Port))
    def connection(self,url_Scheme,url_Netloc):
        if(url_Scheme == 'http'):
            conn = http.client.HTTPConnection(url_Netloc)
        else:
            conn = http.client.HTTPSConnection(url_Netloc)
        return(conn)
    def get_Cookie(self,headers):
        Cookies = []
        for each in headers:
            if(each[0]=='Set-Cookie'):
                Cookies.append(each[1])
        return(Cookies)
    def extract_Cookie_NV(self,Set_Cookie):
        CK = Set_Cookie.split(';')
        regex_CK_attr = re.compile('Max-Age|Expires|Domain|Path|Secure|HttpOnly',re.I)
        len = CK.__len__()
        regex_NV = re.compile('(.*)=(.*)')
        for i in range(0,len):
            m = regex_NV.search(CK[i])
            if(m==None):
                N = CK[i]
                V = ''
            else:
                N = m.group(1)
                V = m.group(2)
            if(regex_CK_attr.search(N)):
                pass
            else:
                return((N,V))
    def creat_Cookie(self,Set_Cookies):
        NV_list = []
        for each in Set_Cookies:
            NV_list.append(self.extract_Cookie_NV(each))
        CK_header = 'Cookie: '
        for each in NV_list:
            NV_str = '{0}={1}; '.format(each[0],each[1])
            CK_header = ''.join((CK_header,NV_str))
        return(CK_header.rstrip(' ').rstrip(';'))
    def header_To_Tuple(self,cc_Cookie):
        regex_Cookie = re.compile('(.*): (.*)')
        m = regex_Cookie.search(cc_Cookie)
        return((m.group(1),m.group(2)))
    def findall_JScript(self,body,output_file):
        regex_Script = re.compile('<script(.*?)>(.*?)</script>',re.DOTALL)
        regex_Src = re.compile('src=')
        scripts = regex_Script.findall(body.decode('utf-8','ignore'))
        beau_Scripts = {}
        remote_Scripts_TU = {}
        len = scripts.__len__();
        fd = open(output_file,'w+')
        for i in range (0,len):
            beau_Scripts[i+1] = jsbeautifier.beautify(scripts[i][1])
            fd.write('\n//-----{0}------#\n'.format(i+1))
            remote_Scripts_TU[i+1] = scripts[i][0]
            if(regex_Src.search(remote_Scripts_TU[i+1]) == None):
                fd.write('\nlocal_type_:\n{0}\n'.format(remote_Scripts_TU[i+1]))
                fd.write(beau_Scripts[i+1])
                fd.write('\n')
            else:
                fd.write('\nremote_type_src:\n{0}\n'.format(remote_Scripts_TU[i+1]))
            fd.write('\n//-----{0}------#\n'.format(i+1))
        fd.close()
        return((beau_Scripts,remote_Scripts_TU))
    def build_Headers_Dict(self,H_string,SP):
        headers = {}
        regex_H = re.compile('(.*): (.*)')
        sp_HS = H_string.split(SP)
        for i in range(0,sp_HS.__len__()):
            m = regex_H.search(sp_HS[i])
            HN = m.group(1)
            HV = m.group(2)
            headers[HN] = HV
        return(headers)
    def expand_Headers_Dict(self,Cheaders,ex_String_List):
        new_Cheaders = {}
        for each in Cheaders:
            new_Cheaders[each] = Cheaders[each]
        regex_H = re.compile('(.*): (.*)')
        for each in ex_String_List:
            m = regex_H = re.compile('(.*): (.*)')
            new_Cheaders[m.group(1)] = m.group(2)
        return(new_Cheaders)
    def build_Body_String(self,KL,KV):
        body = {}
        len = KL.__len__()
        for i in range(0,len):
            body[KL[i]] = KV[i]
        return(urllib.parse.urlencode(body))
    def stepping_Req(self,conn,method,url_Path,cheaders={},cbody=None):
        conn.request(method,url_Path,headers=cheaders,body=cbody)
        return(conn)
    def check_Resp_Headers(self,rheaders,header,HV):
        len = rheaders.__len__()
        for i in range(0,len):
            if(rheaders[i][0]==header):
                if(rheaders[i][0]==HV):
                    return(1)
                else:
                    return(0)
        return(-1)
    def check_TCP_state(self,conn):
        LA  = ''.join((conn.sock.getsockname()[0],':',str(conn.sock.getsockname()[1])))
        FA = ''.join((conn.sock.getpeername()[0],':',str(conn.sock.getpeername()[1])))
        egrep_RE_string = ''.join((LA,'[ ]+',FA))
        shell_CMDs = {}
        shell_CMDs[1] = 'netstat -n'
        shell_CMDs[2] = ''.join(('egrep ','"',egrep_RE_string,'"'))
        shell_CMDs[3] = "awk {'print $6'}"
        state = pipe_Shell_CMD(shell_CMDs)[0].decode().strip('\n').strip(' ')
        return(state)
    def stepping_Resp(self,conn,keepalivetimeout,explicit=0):
        resp = conn.getresponse()
        rheaders = resp.getheaders()
        rbody = resp.read()
        rkeepalive = self.check_Resp_Headers(rheaders,'Connection','Keep-Alive')
        if(rkeepalive==-1):
            if(explicit==0):
                time.sleep(keepalivetimeout)
                r_TCP_state = self.check_TCP_state(conn)
                print(r_TCP_state)
                if(r_TCP_state=='ESTABLISHED'):
                    pass
                else:
                    print('TCP STATE {0} ,IMPLICIT CONN RESP MODE, CLOSE CONN'.format(r_TCP_state))
                    conn.close()
            else:
                conn.close()
        elif(rkeepalive==0):
            conn.close()
        else:
            pass
        return((conn,resp,rbody))
    def redirect_To_Location(self,Rheaders):
        if(Rheaders.status == 302):
            return(Rheaders.getheader('Location'))
        else:
            return(None)
    def get_Rheaders_VL_Dict(self,Rheaders):
        Rheaders_Dict = {}
        keys = Rheaders.info().keys()
        values = Rheaders.info().values()
        for i in range(0,keys.__len__()):
            if(keys[i] in Rheaders_Dict):
                Rheaders_Dict[keys[i]].append(values[i])
            else:
                Rheaders_Dict[keys[i]] = [values[i]]
        return(Rheaders_Dict)
    def mobile_User_Agent(self,Cheaders):
        CUA = Cheaders['User-Agent']
        regex_Mobile_UA = re.compile('applewebkit.*mobile.*|windows.*phone.*mobile.*|msie.*touch.*wpdesktop|android.*mobile.*|android.*applewebkit.*',re.I)
        if(regex_Mobile_UA.search(CUA)):
            return(True)
        else:
            return(False)
    def creat_B2I_url(self,Cheaders,Rerirecto_Url):
        regex_B2I = re.compile('bootstrap')
        if(self.mobile_User_Agent(Cheaders)):
            url = regex_B2I.sub('mobile_index',Rerirecto_Url,0)
        else:
            url = regex_B2I.sub('index',Rerirecto_Url,0)
        return(url)
    def crypt_JS_mc(self,num):
        ret=""
        b="0123456789ABCDEF"
        if(num==ord(' ')):
            ret="+"
        elif((num<ord('0')  and num!=ord('-') and num!=ord('.'))|(num<ord('A') and num>ord('9'))|(num>ord('Z') and num<ord('a') and num!=ord('_'))|(num>ord('z'))):
            ret = "%"
            ret = ''.join((ret,b[num // 16]))
            ret = ''.join((ret,b[num % 16]))
        else:
            ret=chr(num)
        return(ret)
    def crypt_JS_m(self,num):
        return(((num&1)<<7)|((num&(0x2))<<5)|((num&(0x4))<<3)|((num&(0x8))<<1)|((num&(0x10))>>1)|((num&(0x20))>>3)|((num&(0x40))>>5)|((num&(0x80))>>7))
    def crypt_JS_md6_encode(self,clear_Text_Passwd):
        encryed_Passwd = "";
        c = 0xbb;
        for i in range(0,clear_Text_Passwd.__len__()):
            c = self.crypt_JS_m(ord(clear_Text_Passwd[i]))^(0x35^(i&0xff));
            encryed_Passwd = ''.join((encryed_Passwd,self.crypt_JS_mc(c)))
        return(encryed_Passwd)
    def decrypt_JS_mc(self,old_Urlquote):
        if(old_Urlquote == '+'):
            return(' ')
        else:
            regex_JS_mc = re.compile('%(.*)')
            m = regex_JS_mc.search(old_Urlquote)
            if(m == None):
                return(ord(old_Urlquote))
            else:
                return(int(old_Urlquote.lstrip('%'),16))
    def split_Encrypt_String(self,encrypted_Passwd):
        len = encrypted_Passwd.__len__()
        cursor = 0
        encry_Dict = {}
        count = 0
        temp = ''
        seq = 1
        while(cursor < len):
            if(encrypted_Passwd[cursor]=='%'):
                temp = encrypted_Passwd[cursor+1:cursor+3]
                encry_Dict[seq] = temp
                cursor = cursor + 3
                temp = ''
            else:
                temp = encrypted_Passwd[cursor]
                encry_Dict[seq] = temp
                cursor = cursor + 1
                temp = ''
            seq = seq + 1
        return(encry_Dict)
    def crypt_JS_md6_decode(self,encrypted_Passwd):
        clear_Text_Passwd = ""
        encry_Dict = self.split_Encrypt_String(encrypted_Passwd)
        len = encry_Dict.__len__()
        for i in range(1,len+1):
            ele_Len = encry_Dict[i].__len__()
            if(ele_Len==2):
                num = int(encry_Dict[i],16)
            else:
                num = ord(encry_Dict[i])
            seq = i - 1
            temp_C = num ^ (0x35^(seq&0xff))
            orig_C = self.crypt_JS_m(temp_C)
            char = chr(orig_C)
            clear_Text_Passwd = ''.join((clear_Text_Passwd,char))
        return(clear_Text_Passwd)
    def decompress_Rbody(self,Rbody,Rheaders):
        if(Rheaders.getheader('Content-Encoding')== 'gzip'):
            cc_Rbody = gzip.decompress(Rbody)
        else:
            cc_Rbody = Rbody
        return(cc_Rbody)
    def header_To_Tuple(self,header_String):
        regex_Header_String = re.compile('(.*?): (.*)')
        m = regex_Header_String.search(header_String)
        return((m.group(1),m.group(2)))
# ------------------------------------------------------------------- # 
def walkon(step,url,Method,soli,default_Port,conn=None,H_string=None,C_headers_Dict=None,C_body=None):
    cc_Soli = soli
    url_Scheme = urllib.parse.urlparse(url).scheme
    url_Netloc = urllib.parse.urlparse(url).netloc
    url_NL_HP = cc_Soli.parse_Url_Netloc(url_Netloc,default_Port)
    url_Netloc_Host = url_NL_HP[0]
    url_Netloc_Port = url_NL_HP[1]
    url_Path = urllib.parse.urlparse(url).path
    url_Params = urllib.parse.urlparse(url).params
    url_Query = urllib.parse.urlparse(url).query
    url_Fragment = urllib.parse.urlparse(url).fragment
    if(step == 1):
        cc_Conn = cc_Soli.connection(url_Scheme,url_Netloc)
    else:
        if(conn.sock == None ):
            conn.close()
            cc_Conn = cc_Soli.connection(url_Scheme,url_Netloc)
        else:
            if(conn==None):
                return((None,'conn'))
            else:
                cc_Conn = conn
    if(H_string==None):
        if(C_headers_Dict==None):
            return((None,'C_headers'))
        else:
            cc_Cheaders = C_headers_Dict
    else:
        cc_Cheaders = cc_Soli.build_Headers_Dict(H_string,'\n')
    if(url_Query == ''):
        cc_Conn = cc_Soli.stepping_Req(cc_Conn,Method,url_Path,cheaders=cc_Cheaders,cbody=C_body)
    else:
        cc_Conn = cc_Soli.stepping_Req(cc_Conn,Method,url_Path+'?'+url_Query,cheaders=cc_Cheaders,cbody=C_body)
    cc_Resp = cc_Soli.stepping_Resp(cc_Conn,0,explicit=0)
    cc_Conn = cc_Resp[0]
    cc_Rheaders = cc_Resp[1]
    cc_Rbody = cc_Resp[2]
    cc_Rbody = cc_Soli.decompress_Rbody(cc_Rbody,cc_Rheaders)
    cc_Soli.findall_JScript(cc_Rbody,'s{0}'.format(step)) 
    return((step+1,cc_Conn,cc_Rheaders,cc_Rbody))


