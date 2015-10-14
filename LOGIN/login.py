import time
import sys
import os
import navegador as nave
import websocket
from websocket import create_connection
import urllib
import re
import random
from lxml import etree
from io import StringIO, BytesIO
import lxml.html
import collections
import math
import datetime

def display_list(target):
    t_len = target.__len__()
    if(type(target) == type([])):
        for i in range(0,t_len):
            print("array\t{0}\t{1}".format(i,target[i]))
    elif(type(target) == type({})):
        for key in target:
            print("dict\t{0}\t{1}".format(key,target[key]))
    elif(type(target) == type(())):
        for i in range(0,t_len):
            print("turple\t{0}\t{1}".format(i,target[i]))
    else:
        print(target)



def write_to_file(**kwargs):
    fd = open(kwargs['fn'],kwargs['op'])
    fd.write(kwargs['content'])
    fd.close()

def get_signin_link_href(html_text):
    root = etree.HTML(html_text)
    eles = root.xpath('//p[@class="signin-link"]/a')
    href = collections.OrderedDict(eles[0].items())['href']
    return(href)

def get_already_member_prompt_href(html_text):
    root = etree.HTML(html_text)
    eles = root.xpath('//p[@id="already-member-prompt"]/a')
    href = collections.OrderedDict(eles[0].items())['href']
    return(href)
    
def get_hreflangs(html_text):
    root = etree.HTML(html_text)
    eles = root.xpath('//link[@rel="alternate" and @hreflang]')
    eles_len = eles.__len__()
    hrefs = {}
    for i in range(0,eles_len):
        ele = eles[i]
        hreflang = collections.OrderedDict(ele.items())['hreflang']
        hrefs[hreflang] = collections.OrderedDict(ele.items())['href']
    return(hrefs)


def jsRandomCalculator_f3(v1, v2, email):
    email_len = email.__len__()
    v3 = 0
    for i in range(0,email_len):
        char_code = ord(email[i])
        shift = (5 * i) % 32
        offset = char_code << shift
        offset = offset % (2**32)
        if(offset > 0x7fffffff):
            offset = offset - 2 **32
        else:
            offset = offset
        v3 = v3 + offset
    rslt = (v1 * v2 * v3) % 1000000007
    return(rslt)

def jsRandomCalculator_f2(vs, ts):
    sum = vs[0] + vs[1]
    n = sum % 3000
    m = sum % 10000
    p = ts % 10000
    
    if(n < 1000):
        return(((m + 12345)**2) + ((p + 34567)** 2))
    elif(n < 2000):
        return(((m + 23456)**2) + ((p + 23456)** 2))
    else:
        return(((m + 34567)**2) + ((p + 12345)** 2))

def jsRandomCalculator_f1(vs, ts):
    output = []
    output.append(vs[0] + vs[1] + vs[2])
    output.append((vs[0] % 100 + 30) * (vs[1] % 100 + 30) * (vs[2] % 100 + 30))
    for i in range(0,10):
        output[0] += (output[1] % 1000 + 500) * (ts % 1000 + 500)
        output[1] += (output[0] % 1000 + 500) * (ts % 1000 + 500)
    return(output)

    
def jsRandomCalculator_compute(n, email, ts):
    try:
        vs = n.split(":")
        ts = int(ts)
        vs_len = vs.__len__()
        for i in range(0,vs_len):
            vs[i] = int(vs[i], 10)
        f1_out = jsRandomCalculator_f1(vs, ts)
        f2_out = jsRandomCalculator_f2(f1_out, ts)
        if(f1_out[0] % 1000 > f1_out[1] % 1000):
            v = f1_out[0]
        else:
            v = f1_out[1]
        return(jsRandomCalculator_f3(v, f2_out, email))
    except Exception as err:
        return(-1)
    
    
def js_clock_seconds(accuracy):
    accuracy = int(accuracy) - 1
    now = str(time.time())
    now = now.replace('.','')
    now = now[0:accuracy]
    return(int(now))
    
    
def gen_client_n():
    b = []
    for c in range(0,3):
        temp = math.floor(9*(10**8) * random.random()) + 10**8
        b.append(str(temp)) 
    rslt = urllib.parse.quote(':'.join((b[0],b[1],b[2])))
    return(rslt)    
    
def gen_login_post_body(eles,email_address,passwd):
    eles_len = eles.__len__()
    query_dict = {}
    for i in range(0,eles_len):
        ele = eles[i]
        name = collections.OrderedDict(ele.items())['name']
        try:
            value = collections.OrderedDict(ele.items())['value']
        except Exception as err:
            if(err == KeyError):
                value = ''
        query_dict[name] = value
    
    query_dict['session_key'] = urllib.parse.quote(email_address)
    query_dict['session_password'] = passwd
    query_dict['client_ts'] = js_clock_seconds(13)
    query_dict['client_n'] = gen_client_n()
    query_dict['client_v'] = '1.0.1'
    query_dict['client_r'] = '%3A'.join((email_address,query_dict['client_n']))
    query_dict['client_output'] = jsRandomCalculator_compute(urllib.parse.unquote(query_dict['client_n']), email_address, query_dict['client_ts'])
    
    return(urllib.parse.urlencode(query_dict))
    
    
    
    
def decode_resp_set_cookie(set_cookie_tuple):
    rslt = {}
    set_cookie_len = set_cookie_tuple.__len__()
    rslt['type'] =  set_cookie_tuple[0]
    content = set_cookie_tuple[1]
    attrs = content.split('; ')
    regex_ck_attr = re.compile('Max-Age|Expires|Domain|Path|Secure|HttpOnly|Version|Comment|Discard|CommentURL',re.I)
    regex_kv = re.compile('(.*)=(.*)')
    for i in range(0,attrs.__len__()):
        kv = attrs[i]
        m_ck_attr = regex_ck_attr.search(kv)
        m_kv = regex_kv.search(kv)
        if(m_ck_attr==None):
            rslt['cookie'] = kv
        else:
            if(m_kv == None):
                key = kv
                value = ''
            else:
                key = m_kv.group(1)
                value = m_kv.group(2)
            rslt[key] = value
    display_list(rslt)
    return(rslt)
    
    
