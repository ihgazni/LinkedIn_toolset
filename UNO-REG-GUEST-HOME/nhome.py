import json
import jsbeautifier as jb




H_string = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36
Accept-Encoding: gzip,deflate,sdch
Accept-Language: zh-CH,zh;q=0.8'''

login_rslt = linkedin_login('XXXXXXXX','XXXXXXXX',H_string)

url = login_rslt['location']


cc_Scrr = nave.walkon(login_rslt['step'],url,'GET',soli=login_rslt['soli'],default_Port=80,conn=login_rslt['conn'],H_string=None,C_headers_Dict=login_rslt['req_head'],C_body=None)
cc_Step = cc_Scrr[0]
cc_Conn = cc_Scrr[1]
resp_head = cc_Scrr[2]
resp_body = cc_Scrr[3]

write_to_file(fn='nhome.html',content=resp_body,op='wb+')
html_text = resp_body.decode('utf-8')

root = etree.HTML(html_text)

def get_code_via_id(root,id):
    selector = ''.join(('//code[@id','=','"',id,'"',']'))
    eles = root.xpath(selector)
    children = eles[0].getchildren()
    comment = children[0]
    rslt_dict = json.loads(comment.text)
    print(jb.beautify(comment.text))
    return(rslt_dict)
    

nhome = get_code_via_id(root,"ozfeed-templates/feed-content")

#get_dict_value_from_full_key_path(nhome,"updates/useRmvWithMentions")
def get_dict_value_from_full_key_path(d,full_key_path):
    full_key_path = full_key_path.strip("/")
    if(full_key_path == ''):
        return(d)
    keys = full_key_path.split("/")
    now = d
    klen = keys.__len__()
    for i in range(0,klen):
        try:
            now = now.__getitem__(keys[i])
        except Exception as err:
            now = now.__getitem__(int(keys[i]))
    return(now)


#get_all_sons_full_key_path
def get_all_sons_full_key_path_list(d,full_key_path):
    all_sons_full_key_path_list = []
    value = get_dict_value_from_full_key_path(d,full_key_path)
    value_type = type(value)
    if(value_type == type([])):
        v_len = value.__len__()
        for i in range(0,v_len):
            kp = ''.join((full_key_path.rstrip("/"),"/",str(i)))
            all_sons_full_key_path_list.append(kp)
    elif(value_type == type({})):
        v_len = value.__len__()
        for each in value:
            kp = ''.join((full_key_path.rstrip("/"),"/",each))
            all_sons_full_key_path_list.append(kp)
    else:
        pass
    return(all_sons_full_key_path_list)

def list_to_lsd(l):
    lsd = {}
    llen = l.__len__()
    for i in range(0,llen):
        lsd[i] = l[i]
    return(lsd)
# 

#dict_array_description 
#dora = nhome
def dict_array_description(dora):
    description_dict = {}
    all_leafs = 0
    unhandled_now = {0:''}
    unhandled_next = {}
    while(all_leafs == 0):
        temp = 0
        description_dict_len = description_dict.__len__()
        description_dict[description_dict_len] = {}
        desc_layer_dict = description_dict[description_dict_len]
        unhandled_now_len = unhandled_now.__len__()
        for i in range(0,unhandled_now_len):
            value = get_dict_value_from_full_key_path(dora,unhandled_now[i])
            value_type = type(value)
            desc_layer_dict_len = desc_layer_dict.__len__()
            desc_layer_dict[desc_layer_dict_len] = unhandled_now[i]
            if( value_type == type([])):
                all_sons_fkp_list = get_all_sons_full_key_path_list(dora,unhandled_now[i])
                llen = all_sons_fkp_list.__len__()
                for i in range(0,llen):
                    unhandled_next_len = unhandled_next.__len__()
                    unhandled_next[unhandled_next_len] = all_sons_fkp_list[i]
                temp = temp | 1
            elif(value_type == type({})):
                all_sons_fkp_list = get_all_sons_full_key_path_list(dora,unhandled_now[i])
                llen = all_sons_fkp_list.__len__()
                for i in range(0,llen):
                    unhandled_next_len = unhandled_next.__len__()
                    unhandled_next[unhandled_next_len] = all_sons_fkp_list[i]
                temp = temp | 1
            else:
                temp = temp | 0
        if(temp == 0):
            all_leafs = 1
        unhandled_now = unhandled_next
        unhandled_next = {}
    return(description_dict)

# description_dict = dict_array_description(dora)

def pdesc(description_dict):
    for i in range(0,description_dict.__len__()):
        parray(description_dict[i])
        boundary = ''.join(('-'*20,'\n'))
        print((boundary * (i+1)).strip('\n'))

def is_parent(son,parent):
    son = son.rstrip('/')
    parent = parent.rstrip('/')
    sks = son.split('/')
    pks = parent.split('/')
    if(pks.__len__() >= sks.__len__()):
        return(0)
    if((sks.__len__() - pks.__len__()) == 1):
        for i in range(0,pks.__len__()):
            if(sks[i] == pks[i]):
                pass
            else:
                return(0)
        return(1)
    else:
        return(0)

def get_parent(son):
    if(son == ''):
        son = '/'
    regex = re.compile('(.*)/(.*?)')
    m = regex.search(son)
    return(m.group(1))

def get_rel(abs):
    if(abs == ''):
        abs = '/'
    regex = re.compile('(.*)/([^/]*)')
    m = regex.search(abs)
    return(m.group(2))

# tree_desc
def get_desc_parent_dict(description_dict):
    desc_len = description_dict.__len__()
    parent_dict = {}
    for i in range(0,desc_len):
        each_level_len = description_dict[i].__len__()
        next_level_cursor = 0
        if(i == 0):
            parent_dict[i] = {}
            parent_dict[i+1] = {}
            next_level_len = description_dict[i+1].__len__()
        elif(i == (desc_len - 1)):
            pass
        else:
            parent_dict[i+1] = {}
            next_level_len = description_dict[i+1].__len__()
        for j in range(0,each_level_len):
            if(i == 0):
                parent_dict[i][j] = -1
            if(i == (desc_len - 1)):
                pass
            else:
                for k in range(next_level_cursor,next_level_len):
                    if(is_parent(description_dict[i+1][k],description_dict[i][j])):
                        parent_dict[i+1][k] = j
                        next_level_cursor = next_level_cursor + 1
                    else:
                        break
    return(parent_dict)



# ---------------- #
def tree_desc(description_dict):
    parent_dict = get_desc_parent_dict(description_dict)
    total_count = 0
    desc_len = description_dict.__len__()
    lvseq_dict = {}
    travel_sign_dict = {}
    for i in range(0,desc_len):
        lvseq_dict[i] = 0
        travel_sign_dict[i] = {}
        each_level_len = description_dict[i].__len__()
        for j in range(0,each_level_len):
            travel_sign_dict[i][j] = 0
            total_count = total_count + 1
    indent = '    '
    text = ''
    prev_level = -1
    prev_seq = -1
    curr_level = 0
    curr_seq = 0
    count = 0
    deep_search_path = []
    while(count < total_count):
        each_level_len = description_dict[curr_level].__len__()
        full_key_path = description_dict[curr_level][curr_seq]
        if(curr_level > prev_level):
            text = ''.join((text,'\n',indent * curr_level,full_key_path))
            curr_location = (curr_level,curr_seq)
            deep_search_path.append(curr_location)
            count = count + 1
            lvseq_dict[curr_level] = curr_seq
            if(get_all_sons_full_key_path_list(nhome,full_key_path) == []):
                travel_sign_dict[curr_level][curr_seq] = 2
                if(curr_seq < (each_level_len - 1)):
                    prev_seq = curr_seq
                    prev_level = curr_level
                    next_seq = curr_seq + 1
                    cond = (parent_dict[curr_level][curr_seq] == parent_dict[curr_level][next_seq])
                    lvseq_dict[curr_level] = curr_seq + 1
                    if(cond):
                        curr_level = curr_level
                        curr_seq = curr_seq + 1
                    else:
                        curr_level = curr_level - 1
                        curr_seq = lvseq_dict[curr_level]
                else:
                    prev_seq = curr_seq
                    prev_level = curr_level
                    curr_level = curr_level - 1
                    curr_seq = lvseq_dict[curr_level]
            else:
                prev_level = curr_level 
                curr_level = curr_level + 1
                prev_seq = curr_seq
                curr_seq = lvseq_dict[curr_level]
                travel_sign_dict[curr_level][curr_seq] = 1
        elif(curr_level == prev_level):
            text = ''.join((text,'\n',indent * curr_level,full_key_path))
            curr_location = (curr_level,curr_seq)
            deep_search_path.append(curr_location)
            count = count + 1
            lvseq_dict[curr_level] = curr_seq
            if(get_all_sons_full_key_path_list(nhome,full_key_path) == []):
                travel_sign_dict[curr_level][curr_seq] = 2
                if(curr_seq < (each_level_len - 1)):
                    prev_seq = curr_seq
                    prev_level = curr_level
                    next_seq = curr_seq + 1
                    cond = (parent_dict[curr_level][curr_seq] == parent_dict[curr_level][next_seq])
                    lvseq_dict[curr_level] = curr_seq + 1
                    if(cond):
                        curr_level = curr_level
                        curr_seq = curr_seq + 1
                    else:
                        curr_level = curr_level - 1
                        curr_seq = lvseq_dict[curr_level]
                else:
                    prev_seq = curr_seq
                    prev_level = curr_level
                    curr_level = curr_level - 1
                    curr_seq = lvseq_dict[curr_level]
            else:
                prev_level = curr_level 
                curr_level = curr_level + 1
                prev_seq = curr_seq
                curr_seq = lvseq_dict[curr_level]
                travel_sign_dict[curr_level][curr_seq] = 1
        else:
            travel_sign_dict[curr_level][curr_seq] = 2
            if(curr_seq < (each_level_len - 1)):
                prev_seq = curr_seq
                prev_level = curr_level
                next_seq = curr_seq + 1
                cond = (parent_dict[curr_level][curr_seq] == parent_dict[curr_level][next_seq])
                lvseq_dict[curr_level] = curr_seq + 1
                if(cond):
                    curr_level = curr_level
                    curr_seq = curr_seq + 1
                else:
                    curr_level = curr_level - 1
                    curr_seq = lvseq_dict[curr_level]
            else:
                prev_seq = curr_seq
                prev_level = curr_level
                curr_level = curr_level - 1
                curr_seq = lvseq_dict[curr_level]
    rslt = {}
    rslt['text'] = text
    rslt['parent_dict'] = parent_dict
    rslt['deep_search_path'] =  deep_search_path
    return(rslt)


def dynamic_indent(deep_search_path,description_dict,full_path_display,fr='',to=''):
    if(fr == ''):
        fr = 0
    text = ''
    dsp_len = deep_search_path.__len__()
    if(to == ''):
        to = dsp_len
    for i in range(0,dsp_len):
        x = deep_search_path[i][0]
        y = deep_search_path[i][1]
        ele = description_dict[x][y]
        if(full_path_display):
            line = ele
        else:
            indent = get_parent(ele)
            indent = indent.replace('/','')
            indent = ' ' * indent.__len__()
            rel = get_rel(ele)
            line = ''.join((indent,rel))
        if((i >= fr) & (i <= to)):
            text = ''.join((text,'\n',line))
    return(text)

# dynamic_indent(deep_search_path,description_dict,0)
# dynamic_indent(deep_search_path,description_dict,1)


