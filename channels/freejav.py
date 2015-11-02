# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para freejav
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools


__channel__ = "freejav"
__category__ = "X,F"
__type__ = "generic"
__title__ = "Freejav"
__language__ = "ES"


DEBUG = config.get_setting("debug")
    
def isGeneric():
    return True

def mainlist(item):
    logger.info("[freejav.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Censored" , url="http://freejav.us/danh-sach/phim-censored",thumbnail="http://freejav.us/template/images/image-header2.png", plot=""))
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Uncensored" , url="http://freejav.us/danh-sach/phim-uncensored/",thumbnail="http://freejav.us/template/images/image-header2.png", plot=""))    
	
    return itemlist


def lista(item):
    logger.info("[freejav.py] lista")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)                        
    patronvideos ='<div class="poster">.*?<a href="([^"]+)" title="([^"]+)"><img src="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[0]
        scrapedthumbnail = match[2]
        imagen = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="lista2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedthumbnail , plot="" , folder=True) )
 
 
  
  # Extrae la marca de siguiente página
    data = scrapertools.find_single_match(data,'<div class="pagination">(.*?)<div class="block topic">')
    patronvideos ='<span class="currentpage"><span>.*?</span>.*?<a href="([^"]+)">([^"]+)</a>'
    matches2 = re.compile(patronvideos,re.DOTALL).findall(data)
    
    for match in matches2:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        url = urlparse.urljoin("http://freejav.us/",scrapedurl)
        if (DEBUG): logger.info("url=["+scrapedurl+"]")
        itemlist.append( Item(channel=__channel__, action="lista", title="Página " + scrapedtitle , url=url , plot="" , folder=True) )
 
    return itemlist



def lista2(item):
    logger.info("[freejav.py] lista2")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)                        
    patronvideos ='<p class="w_now"><a href="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = item.title
        scrapedurl = match
        scrapedthumbnail = item.thumbnail
        imagen = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="detail", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot="" , folder=True) )

    return itemlist


def detail(item):
    logger.info("[freejav.py] detail")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)


    # Busca los enlaces a los videos de los servidores
    video_itemlist = servertools.find_video_items(data=data)
    for video_item in video_itemlist:
        itemlist.append( Item(channel=__channel__ , action="play" , server=video_item.server, title=video_item.title, url=video_item.url, thumbnail=item.thumbnail, plot=item.plot, folder=False))

    patronvideos ="<span class='logo-server 1'>([^']+):</span>.*?href='([^']+)'>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[0]
        scrapedurl = match[1]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        if scrapedurl != item.url:
            itemlist.append( Item(channel=__channel__, action="detail", title=scrapedtitle , url=scrapedurl , thumbnail="" , plot="" , folder=True) )

    return itemlist