import requests
from bs4 import BeautifulSoup



def volatility ():
    r = requests.get('https://www.myfxbook.com/forex-market/volatility')
    #%% 
    soup = BeautifulSoup(r.text, 'html.parser')
    #%%
    spans = soup.find_all("span")
    
    #%%
    number_spans = [ x for x in spans if x.attrs.get('value') != None ] 
    #%%
    hour_spans = [x for x in number_spans if x.attrs.get('id', [])[-len('TimeScale60'):] == 'TimeScale60' ]
    #%%
    ordered_spans = []
    for x in hour_spans:
        for y in range(len(ordered_spans)):
            if  float(x.attrs.get('value')) >= float(ordered_spans[y].attrs.get('value')):
                ordered_spans = ordered_spans[:y] + [x] + ordered_spans[y:]
                break
        else:
            ordered_spans.append(x)
    #%%
    name_spans = [x.attrs.get('name')[:6] for x in ordered_spans]# -*- coding: utf-8 -*-
    return name_spans


