
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
import copy


def parray(target):
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
    elif(type(target) == type(collections.OrderedDict([('a','b')]))):
        for i in range(0,t_len):
            print("od\t{0}\t{1}\t{2}".format(i,target[i][0],target[i][1]))
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
    rslt = ':'.join((b[0],b[1],b[2]))
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
    
    query_dict['session_key'] = email_address
    query_dict['session_password'] = passwd
    query_dict['client_ts'] = str(js_clock_seconds(13))
    query_dict['client_n'] = gen_client_n()
    query_dict['client_v'] = '1.0.1'
    query_dict['client_r'] = ':'.join((email_address,query_dict['client_n']))
    query_dict['client_output'] = jsRandomCalculator_compute(urllib.parse.unquote(query_dict['client_n']), email_address, query_dict['client_ts'])
    query_dict['isJsEnabled'] = 'true'
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
    parray(rslt)
    return(rslt)

def which_time_format(date_value):
    month = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
    weekday = 'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'
    wkday = 'Mon|Tue|Wed|Thu|Fri|Sat|Sun'
    rfc1123 = ''.join(("(",wkday,")",", ","[0-9]{2} ","(",month,")"," [0-9]{4} ","[0-9]{2}:[0-9]{2}:[0-9]{2} ","GMT"))
    regex_rfc1123 = re.compile(rfc1123)
    rfc1123_hypen = ''.join(("(",wkday,")",", ","[0-9]{2}-","(",month,")","-[0-9]{4} ","[0-9]{2}:[0-9]{2}:[0-9]{2} ","GMT"))
    regex_rfc1123_hypen = re.compile(rfc1123_hypen)
    rfc850 = ''.join(("(",weekday,")",", ","[0-9]{2}-","(",month,")","-[0-9]{2} ","[0-9]{2}:[0-9]{2}:[0-9]{2} ","GMT"))
    regex_rfc850 = re.compile(rfc850)
    rfc850_a = ''.join(("(",wkday,")",", ","[0-9]{2}-","(",month,")","-[0-9]{2} ","[0-9]{2}:[0-9]{2}:[0-9]{2} ","GMT"))
    regex_rfc850_a = re.compile(rfc850_a)
    asctime = ''.join(("(",wkday,")"," ","(",month,")","(( [0-9]{2})|(  [0-9]{1}))"," ","[0-9]{2}:[0-9]{2}:[0-9]{2} ","[0-9]{4}"))
    regex_asctime = re.compile(asctime)
    if(regex_rfc1123.search(date_value)):
        return('rfc1123_date')
    elif(regex_rfc1123_hypen.search(date_value)):
        return('rfc1123_hypen_date')
    elif(regex_rfc850.search(date_value)):
        return('rfc850_date')
    elif(regex_rfc850_a.search(date_value)):
        return('rfc850_date_a')
    elif(regex_asctime.search(date_value)):
        return('asctime_date')
    else:
        return(None)

def http_cookie_expired(expire):
    #python if not implement tzinfo or use pytz module, the timezone info will not be calculated
    now = datetime.datetime.now()
    now = time.mktime(now.timetuple())
    utcnow = datetime.datetime.utcnow()
    utcnow = time.mktime(utcnow.timetuple())
    diff = utcnow - now
    wtf = which_time_format(expire)
    if(wtf == "rfc1123_date"):
        expire =  time.strptime(expire, '%a, %d %b %Y %H:%M:%S %Z')
    elif(wtf == "rfc1123_hypen_date"):
        expire =  time.strptime(expire, '%a, %d-%b-%Y %H:%M:%S %Z')
    elif(wtf == "rfc850_date"):
        expire =  time.strptime(expire, '%A, %d-%b-%y %H:%M:%S %Z')
    elif(wtf == "rfc850_date_a"):
        expire =  time.strptime(expire, '%a, %d-%b-%y %H:%M:%S %Z')
        
    expire =  time.mktime(expire)
    expire = expire + diff
    if(utcnow > expire):
        return(1)
    else:
        return(0)

def http_cookie_overdue(cookie_dict):
# If a cookie has both the Max-Age and the Expires attribute, the Max-
# Age attribute has precedence and controls the expiration date of the
# cookie.  If a cookie has neither the Max-Age nor the Expires
# attribute, the user agent will retain the cookie until "the current
# session is over" (as defined by the user agent).
    rslt = {}
    rslt['errors'] = []
    if('Max-Age' in cookie_dict):
        if(int(cookie_dict['Max-Age']) <= 0):
            rslt['errors'].append('Max-Age')
    else:
        if('Expires' in cookie_dict):
            if(http_cookie_expired(cookie_dict['Expires'])):
                rslt['errors'].append('Expires')
    if(rslt['errors'].__len__() == 0):
        rslt['valid'] = 1
    else:
        rslt['valid'] = 0
    return(rslt)

def http_cookie_outof_domain(cookie_dict,**kwargs):
# 4.1.2.3.  The Domain Attribute
    # The Domain attribute specifies those hosts to which the cookie will
    # be sent.  For example, if the value of the Domain attribute is
    # "example.com", the user agent will include the cookie in the Cookie
    # header when making HTTP requests to example.com, www.example.com, and
    # www.corp.example.com.  (Note that a leading %x2E ("."), if present,
    # is ignored even though that character is not permitted, but a
    # trailing %x2E ("."), if present, will cause the user agent to ignore
    # the attribute.)  If the server omits the Domain attribute, the user
    # agent will return the cookie only to the origin server.
    # WARNING: Some existing user agents treat an absent Domain
    # attribute as if the Domain attribute were present and contained
    # the current host name.  For example, if example.com returns a Set-
    # Cookie header without a Domain attribute, these user agents will
    # erroneously send the cookie to www.example.com as well.
    # The user agent will reject cookies unless the Domain attribute
    # specifies a scope for the cookie that would include the origin
    # server.  For example, the user agent will accept a cookie with a
    # Domain attribute of "example.com" or of "foo.example.com" from
    # foo.example.com, but the user agent will not accept a cookie with a
    # Domain attribute of "bar.example.com" or of "baz.foo.example.com".
    # NOTE: For security reasons, many user agents are configured to reject
    # Domain attributes that correspond to "public suffixes".  For example,
    # some user agents will reject Domain attributes of "com" or "co.uk".
    from_url = kwargs['from_url']
    to_url = kwargs['to_url']
    origin_server = urllib.parse.urlparse(from_url).netloc
    to_domain = urllib.parse.urlparse(to_url).netloc
    if('Domain' in cookie_dict):
        domain = cookie_dict['Domain'].lstrip('.')
        regex_str = ''.join((domain,'$'))
        regex_domain = re.compile(regex_str)
        if(regex_domain.search(to_domain) == None):
            return(1)
        else:
            return(0)
    else:
        if(origin_server == to_domain):
            return(0)
        else:
            return(1)

def http_cookie_outof_path(cookie_dict,**kwargs):
# 4.1.2.4.  The Path Attribute
   # The scope of each cookie is limited to a set of paths, controlled by
   # the Path attribute.  If the server omits the Path attribute, the user
   # agent will use the "directory" of the request-uri’s path component as
   # the default value.  (See Section 5.1.4 for more details.)
   # The user agent will include the cookie in an HTTP request only if the
   # path portion of the request-uri matches (or is a subdirectory of) the
   # cookie’s Path attribute, where the %x2F ("/") character is
   # interpreted as a directory separator.
   # Although seemingly useful for isolating cookies between different
   # paths within a given host, the Path attribute cannot be relied upon
   # for security (see Section 8).
    from_url = kwargs['from_url']
    from_path = urllib.parse.urlparse(from_url).path
    to_url = kwargs['to_url']
    to_path = urllib.parse.urlparse(to_url).path
    if('Path' in cookie_dict):
        path = cookie_dict['Path']
    else:
        path = from_path
    regex_str = ''.join(('^',path))
    regex_path = re.compile(regex_str)
    if(regex_path.search(to_path) == None):
        return(1)
    else:
        return(0)

def http_cookie_only_for_https(cookie_dict,**kwargs):
    to_url = kwargs['to_url']
    url_scheme = urllib.parse.urlparse(to_url).scheme
    regex_secure = re.compile("Secure",re.I)
    secure_inside = 0
    for key in cookie_dict:
        if(regex_secure.search(key) == None):
            pass
        else:
            secure_inside = 1
            break
    if(secure_inside == 0):
        return(1)
    else:
        if(url_scheme == "https"):
            return(1)
        else:
            return(0)

def http_cookie_not_for_apps(cookie_dict,**kwargs):
    regex_http_only = re.compile("HttpOnly",re.I)
    for key in cookie_dict:
        if(regex_http_only.search(key) == None):
            pass
        else:
            return 1
    return 0

def select_headers_via_key(headers_turple_array,key):
    arr = headers_turple_array
    arr_len = arr.__len__()
    rslt = []
    for i in range(0,arr_len):
        k = arr[i][0]
        v = arr[i][1]
        if(k == key):
            temp = (k,v)
            print(temp)
            rslt.append(temp)
    return(rslt)

def is_cookie_valid_for_send(set_cookie_tuple,from_url,to_url):
    cookie_dict = decode_resp_set_cookie(set_cookie_tuple)
    not_overdue = http_cookie_overdue(cookie_dict)['valid']
    in_domain = not(http_cookie_outof_domain(cookie_dict,from_url=from_url,to_url=to_url))
    in_path = not(http_cookie_outof_path(cookie_dict,from_url=from_url,to_url=to_url))
    ok_scheme = http_cookie_only_for_https(cookie_dict,to_url=to_url)
    if(not_overdue & in_domain & in_path & ok_scheme):
        return(1)
    else:
        return(0)

def select_valid_cookies_from_resp (req_head,resp_head,from_url,to_url):
    arr = resp_head.getheaders()
    arr_cookies = select_headers_via_key(arr,'Set-Cookie')
    arr_cookies_len = arr_cookies.__len__()
    if(req_head=={}):
        last = "Cookie: "
    else:
        req_head_ck_dict = cookie_str_to_dict(req_head['Cookie'])
        new_ck_dict = {}
        for k in req_head_ck_dict:
            if(key_in_arr_cookies(k,arr_cookies)):
                pass
            else:
                new_ck_dict[k] = req_head_ck_dict[k]
        new_ck_str = cookie_dict_to_str(new_ck_dict)
        last = ''.join(("Cookie: ",new_ck_str))
    new = last
    for i in range(0,arr_cookies_len):
        if(is_cookie_valid_for_send(arr_cookies[i],from_url,to_url)):
            cookie_dict = decode_resp_set_cookie(arr_cookies[i])
            new = ''.join((new,"; "))
            new = ''.join((new,cookie_dict['cookie']))
    new.rstrip(" ")
    new.rstrip(";")
    if(new == "Cookie: "):
        return("")
    else:
        return(new.replace('Cookie: ; ','Cookie: '))

def url_to_fn(url):
    netloc = urllib.parse.urlparse(url).netloc
    fn = netloc.replace(".","_")
    fn = ''.join((fn,".","html"))
    return(fn)

def set_rt_cookie(url):
    r=re.sub("#.*","",url)
    r=urllib.parse.quote(url)
    r=r.replace("/","%2F")
    n=js_clock_seconds(13)
    rslt = ''.join(("r=",str(r),"&","s=",str(n)))
    return(rslt)

def gen_plist():
    boomerangStart = js_clock_seconds(13)
    boomerangEnd = boomerangStart + 7
    navigationStart = boomerangStart - 15000
    fetchStart = boomerangStart - 13712
    domainLookupStart = boomerangStart - 13712
    domainLookupEnd = boomerangStart - 13712
    connectStart = boomerangStart - 13712
    connectEnd = boomerangStart - 13712
    requestStart = boomerangStart - 13705
    responseStart = boomerangStart - 6042
    responseEnd =  boomerangStart - 6038
    domLoading =  boomerangStart - 6034
    domInteractive =  boomerangStart - 5115
    domContentLoadedEventStart = boomerangStart - 5115
    domContentLoadedEventEnd = boomerangStart - 5070
    domComplete = boomerangStart - 284
    loadEventStart = boomerangStart - 284
    loadEventEnd = boomerangStart - 273
    nativeTimings_start = boomerangStart - 15000
    plist = {
        "totalDomContentLoadTime": 9885,
        "dnsTime": 0,
        "connectTime": 0,
        "firstByteTime": 7670,
        "pageDownloadTime": 4,
        "frontendTime": 5754,
        "navigationTimingApi": "true",
        "pageKey": "uno-reg-guest-home",
        "boomerangStart": boomerangStart,
        "boomerangEnd": boomerangEnd,
        "redirectCount": 0,
        "navigationType": 0,
        "navigationStart": navigationStart,
        "unloadEventStart": 0,
        "unloadEventEnd": 0,
        "redirectStart": 0,
        "redirectEnd": 0,
        "fetchStart": fetchStart,
        "domainLookupStart": domainLookupStart,
        "domainLookupEnd": domainLookupEnd,
        "connectStart": connectStart,
        "connectEnd": connectEnd,
        "requestStart": requestStart,
        "responseStart": responseStart,
        "responseEnd": responseEnd,
        "domLoading": domLoading,
        "domInteractive": domInteractive,
        "domContentLoadedEventStart": domContentLoadedEventStart,
        "domContentLoadedEventEnd": domContentLoadedEventEnd,
        "domComplete": domComplete,
        "loadEventStart": loadEventStart,
        "loadEventEnd": loadEventEnd,
        "timeDone": 15003,
        "timePage": 8945,
        "timeResponse": 6058,
        "timeSource": "navigation",
        "isSSL": 1,
        "nativeTimings": [{
            "timingName": "_PageNavigationStart",
            "start": nativeTimings_start,
            "timingPageKey": "uno-reg-guest-home"
        }]
    }
    rslt=plist.__str__().replace(" ","")
    rslt=''.join(("plist=",rslt))
    return(rslt)

def pcookie(cookie_str):
    cookie_str = cookie_str.replace("Cookie: ","")
    eles = cookie_str.split('; ')
    parray(eles)
    return(eles)

def urldecode(encoded_str):
    eles = encoded_str.split("&")
    eles_len = eles.__len__()
    r1 = {}
    for i in range(0,eles_len):
        kv = eles[i]
        if("=" in kv):
            kv_arr = kv.split("=")
            k=kv_arr[0]
            v=kv_arr[1]
            k=urllib.parse.unquote(k)
            v=urllib.parse.unquote(v)
            r1[k] = v
        else:
            k = kv
            v = {}
            k=urllib.parse.unquote(k)
            r1[k] = v
    return(r1)

def urlencode(decoded_dict):
    eles = decoded_dict
    eles_len = eles.__len__()
    r1_dict = {}
    r2_str = ""
    for k in eles:
        if(type(eles[k]) == type({})):
            r2_str = ''.join((r2_str,"&",k))
        else:
            r1_dict[k] = eles[k]
    rslt_str = urllib.parse.urlencode(r1_dict)
    rslt_str = ''.join((rslt_str,r2_str))
    rslt_str = rslt_str.lstrip("&")
    return(rslt_str)

def cookie_str_to_dict(cookie_str):
    cookie_dict = {}
    eles = cookie_str.split("; ")
    eles_len = eles.__len__()
    regex = re.compile("(.*?)=(.*)")
    for i in range(0,eles_len):
        m = regex.search(eles[i])
        k=m.group(1)
        v=m.group(2)
        cookie_dict[k] = v
    return(cookie_dict)

def cookie_dict_to_str(cookie_dict):
    cookie_str = ""
    for k in cookie_dict:
        cookie_str = ''.join((cookie_str,k,"=",cookie_dict[k],"; "))
    cookie_str = cookie_str.rstrip(" ")
    cookie_str = cookie_str.rstrip(";")
    return(cookie_str)

def key_in_arr_cookies(key,arr_cookies):
    ptrn = ''.join((key,"="))
    arr_cookies_len = arr_cookies.__len__()
    for i in range(0,arr_cookies_len):
        if(ptrn in arr_cookies[i][1]):
            return(1)
    return(0)

def noCache(url):
    try:
        q = url.index("?")
    except Exception as err:
        print(err)
        url = ''.join((url,"?"))
    else:
        url = ''.join((url,"&"))
    url = ''.join((url+ "_" + str(js_clock_seconds(13))))
    return(url)

def get_tree_id(html_text):
    root = etree.HTML(html_text)
    eles = root.xpath('//meta[@name="treeID"]')
    od = collections.OrderedDict(eles[0].items())
    return(od['content'])

def gen_ua_error_data():
    errors_codes = {
        "FZ_CACHE_MISS": 601,
        "FZ_EMPTY_NODE": 602,
        "FZ_DUST_RENDER": 603,
        "FZ_DUST_CHUNK": 604,
        "FZ_DUST_MISSING_TL": 605,
        "FZ_RENDER": 606,
        "FZ_XHR_BAD_STATUS": 607,
        "FZ_XHR_BAD_CONTENT_TYPE": 608,
        "FZ_JSON_PARSE": 609,
        "CTRL_INIT": 701,
        "RUM_CDN_ID_ERROR": 801,
        "RUM_POP_ID_ERROR": 802,
        "RUM_POP_BEACONS_ERROR": 803,
        "HP_STREAM_SERVER_ERROR": 900,
        "HP_STREAM_JS_EXCEPTION": 901
    }
    data={
        "code":"701",
        "message":"object is not a function",
        "unique":"Login",
        "originTreeId":originTreeId,
        "appName":"uas",
        "pageKey":"uas-consumer-login-internal"
     }
    rslt=data.__str__().replace(" ","")
    rslt=''.join(("data=",rslt))
    return(rslt)









def linkedin_login(email_address,passwd):
    H_string = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: zh-CH,zh;q=0.8'''
    cc_Soli = nave.solicitud()
    url = {}
    url[1] = "https://www.linkedin.com/"
    cc_Scrr = nave.walkon(1,url[1],'GET',soli=cc_Soli,default_Port=80,conn=None,H_string=H_string,C_headers_Dict=None,C_body=None)
    cc_Step = cc_Scrr[0]
    cc_Conn = cc_Scrr[1]
    resp_head = cc_Scrr[2]
    resp_body = cc_Scrr[3]
    write_to_file(fn=url_to_fn(url[1]),content=resp_body,op='wb+')
    html_text = resp_body.decode('utf-8')
    signin_link_href = get_signin_link_href(html_text)
    req_head = {}
    resp_cookie_str = select_valid_cookies_from_resp (req_head,resp_head,url[1],signin_link_href)
    req_cookie_str = resp_cookie_str
    curr_head_string = ''.join((H_string,'\n',req_cookie_str))
    req_head = cc_Soli.build_Headers_Dict(curr_head_string,'\n')
    req_head['Referer'] = url[1]
    print('stage_1')
    url[5] = signin_link_href
    cc_Scrr = nave.walkon(cc_Step,url[5],'GET',soli=cc_Soli,default_Port=80,conn=cc_Conn,H_string=None,C_headers_Dict=req_head,C_body=None)
    cc_Step = cc_Scrr[0]
    cc_Conn = cc_Scrr[1]
    resp_head = cc_Scrr[2]
    resp_body = cc_Scrr[3]
    from_url = url[1]
    to_url = url[5]
    resp_cookie_str = select_valid_cookies_from_resp (req_head,resp_head,from_url,to_url)
    req_cookie_str = resp_cookie_str
    curr_head_string = ''.join((H_string,'\n',req_cookie_str))
    req_head = cc_Soli.build_Headers_Dict(curr_head_string,'\n')
    req_head['Referer'] = url[5]
    req_head['Content-Type'] = 'application/x-www-form-urlencoded'
    write_to_file(fn='p5.html',content=resp_body,op='wb+')
    html_text = resp_body.decode('utf-8')
    root = etree.HTML(html_text)
    eles = root.xpath('//form[@name="login"]')
    od = collections.OrderedDict(eles[0].items())
    action = od['action']
    method = od['method']
    eles = root.xpath('//form[@name="login"]//input')
    req_body = gen_login_post_body(eles,email_address,passwd)
    print('stage_2')
    url[7] = action
    from_url = url[1]
    to_url = action
    cc_Scrr = nave.walkon(cc_Step,url[7],method,soli=cc_Soli,default_Port=80,conn=cc_Conn,H_string=None,C_headers_Dict=req_head,C_body=req_body)
    cc_Step = cc_Scrr[0]
    cc_Conn = cc_Scrr[1]
    resp_head = cc_Scrr[2]
    resp_body = cc_Scrr[3]
    from_url = url[1]
    to_url = url[7]
    resp_cookie_str = select_valid_cookies_from_resp (req_head,resp_head,from_url,to_url)
    req_cookie_str = resp_cookie_str
    curr_head_string = ''.join((H_string,'\n',req_cookie_str))
    req_head = cc_Soli.build_Headers_Dict(curr_head_string,'\n')
    rslt = {}
    rslt['req_head']=req_head
    rslt['location']=select_headers_via_key(resp_head.getheaders(),'Location')[0][1]
    rslt['conn']=cc_Conn
    rslt['step']=cc_Step
    return(rslt)


#login_rslt = linkedin_login('XXXXXXXX','XXXXXXXX')

