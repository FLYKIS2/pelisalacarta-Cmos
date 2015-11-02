# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para gaypornshare.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

#from pelisalacarta import buscador

__channel__ = "myhdlibrary"
__category__ = "X,F"
__type__ = "generic"
__title__ = "Myhdlibrary"
__language__ = "ES"
SEARCH = 2

DEBUG = config.get_setting("debug")
    
def isGeneric():
    return True

def mainlist(item):
    logger.info("[Myhdlibrary.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Todas las Películas" , url="http://myhdlibrary.net/",thumbnail="", plot=""))    
    itemlist.append( Item(channel=__channel__, title="Buscar"     , action="search") )	
    return itemlist


def lista(item):
    logger.info("[Myhdlibrary.py] lista")
    itemlist = []

    # Descarga la pagina  
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)
                        
    patronvideos ="<div class='post-thumb in-archive size-large'><a href=\"([^']+)\" title=\"([^']+)\".*?><img width.*?src='([^']+)'"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[0]
        scrapedthumbnail = match[2]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="detail", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedthumbnail , plot="" , folder=True) )
 
  # Extrae la marca de siguiente página
    patronvideos ="<span class='current'>.*?</span><a href='([^']+)' class='inactive' >([^']+)</a>"
    matches2 = re.compile(patronvideos,re.DOTALL).findall(data)
    
    for match2 in matches2:
        scrapedurl = match2[0]
        scrapedtitle = match2[1]

    itemlist.append( Item(channel=__channel__, action="lista", title="Página " + scrapedtitle , url=scrapedurl , folder=True) )
 
    return itemlist



def search(item,texto):
    logger.info("[Myhdlibrary.py] search")
    itemlist = []
    # Descarga la pagina
    itemlist.append(Item(url="http://myhdlibrary.net/?s="+texto))
    return lista(itemlist[0])

def detail(item):
    logger.info("[Myhdlibrary.py] detail")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)

    # Busca los enlaces a los videos de los servidores
    video_itemlist = servertools.find_video_items(data=data)
    for video_item in video_itemlist:
        itemlist.append( Item(channel=__channel__ , action="play" , server=video_item.server, title=item.title+video_item.title, url=video_item.url, thumbnail=item.thumbnail, plot=item.plot, folder=False))

    return itemlist