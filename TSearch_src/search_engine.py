import os
import re
import time
import aiohttp
import asyncio
from aiohttp_socks import SocksConnector, SocksVer
from .config import configuration
from aiohttp.connector import TCPConnector
from concurrent.futures.thread import ThreadPoolExecutor
from bs4 import BeautifulSoup as BS
from lxml import etree
import urllib.parse as up

PROXY = configuration['proxy']
HEADER = configuration['header']

async def get(url, proxy=PROXY):
    connector = SocksConnector.from_url(PROXY, verify_ssl=False)
    if proxy:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, headers={'User-agent':HEADER}) as response:
                return await response.text()
    else:
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url,headers={'User-agent':HEADER}) as response:
                return await response.text()


def deal_with_response(response, list_mode=None, only_text=True, **kwargs):
    soup = BS(response, 'lxml')
    htree = etree.fromstring(response)
    res = {} 
    if list_mode:
        v = list_mode
        # print(v)
        if v.startswith("./") or v.startswith("/"):
            all_items = htree.xpath(v)
            # print(all_items)
            t = {}
            for i in all_items:
                a0 = i.xpath("./a")[0]
                t[' '.join(a0.itertext())] = {
                    'href': a0.attrib['href'],
                    'content':i
                }
            
        else:
            all_items = soup.select(v)
            # print(all_items)
            t = {}
            for i in all_items:
                o = etree.fromstring(i.decode())
                a0 = etree.fromstring(i.select("a")[0].decode())
                t[' '.join(a0.itertext())] = {
                    'href': a0.attrib['href'],
                    'content':o
                }
        return t
    else:
        for k,v in kwargs.items():
            if v.startswith("./") or v.startswith("/"):
                if only_text:
                    res[k] = [' '.join(i.itertext())  for i in htree.xpath(v) if i.text and i.text.strip()]
                else:
                    res[k] = htree.xpath(v)
            else:
                if only_text:
                    res[k] = [i.text for i in soup.select(v) if i.text and i.text.strip()]
                else:
                    res[k] = [etree.fromstring(i.decode()) for i in soup.select(v)]
            
    return res


class Searcher:
    BACK_POCKET = ThreadPoolExecutor(max_workers=12)
    loop = asyncio.get_event_loop()
    def __init__(self, first_key=None):
        self.key = first_key
        n = up.urlparse(configuration['search'])
        self.domain =n.scheme + "://" + n.netloc
        self.external_links = {}
    
    async def result_list(self, search_key=None):
        key =  search_key if search_key else self.key
        assert key is not None
        url = configuration['search'].format(key=key)
        res  = await get(url)
        list_item = deal_with_response(res, list_mode=configuration['list_name'])
        return list_item

    
    async def go_page(self, key):
        assert key is not None
        url = configuration['go_page'].format(key=key)
        res = await get(url)
        output = deal_with_response(res, head=configuration['header'], content=configuration['content'])
        links = deal_with_response(res,only_text=False, elinks = configuration['external_link'])
        
        self.external_links = {}
        for a in links['elinks']:
            l = os.path.basename(a.attrib['href'])
            n = ' '.join(a.itertext())
            self.external_links[n] = l

        return output
    
    def search_in_external(self, key):
        res  = []
        for k in self.external_links:
            if re.search(key,k):
                res.append(k)
        return res

    @classmethod
    def use(cls, name):
        configuration.section = name
        k = configuration.keys
        assert 'search' in k
        assert 'list_name' in  k
        assert 'go_page' in k
        assert 'header' in k
        assert 'external_link' in k
        assert 'content' in k
    
    @classmethod
    def create_searcher(cls, name):
        configuration.section = name
        for name in ['search', 'list_name', 'get_page', 'header', 'content', 'go_page']:
            val = input(name +":")
            assert val is not None
            configuration[name] = val
        configuration.save()
            
            
        

    @classmethod
    def to_do(cls, *tasks):
        loop = cls.loop
        if cls.loop is None:
            loop = asyncio.get_event_loop()
            cls.loop = loop
        else:
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        a = asyncio.gather(*tasks)
        return loop.run_until_complete(a)


if __name__ == "__main__":
    Searcher.use('Wikipedia') 
    s = Searcher() 
    # res = await s.go_page("Radio_Ga_Ga") 
    # res 
    # configuration['content'] 
    configuration['content'] = 'h2,p' 
    # configuration['content'] 
    res = Searcher.to_do(s.go_page("Radio_Ga_Ga"))
    print("First", time.time())
    keys = s.search_in_external('song')[:3]
    fs = [s.go_page(k) for k in keys]
    rr = Searcher.to_do(*fs)
    print("End", time.time())
    print([i['head'] for i in rr])