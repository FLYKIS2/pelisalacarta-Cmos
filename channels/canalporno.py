# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Canalporno
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por Cmos
#------------------------------------------------------------
import cookielib
import urlparse,urllib2,urllib,re
import os
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "canalporno"
__category__ = "X,F"
__type__ = "generic"
__title__ = "Canal Porno"
__language__ = "ES"
__adult__ = "true"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[canalporno.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"      , title="Útimos videos" , url="http://www.canalporno.com/"))
    itemlist.append( Item(channel=__channel__, action="categorias"    , title="Listado Categorias", url="http://www.canalporno.com/categorias/"))
    itemlist.append( Item(channel=__channel__, action="search"    , title="Buscar", url="http://www.canalporno.com/search/?q=%s"))
    return itemlist


def search(item, texto):
    logger.info("[canalporno.py] search")
    itemlist = []

    try:
        item.url = item.url % texto
        item.extra = "cat"
        itemlist.extend(videos(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def videos(item):
    logger.info("[canalporno.py] videos")
    data = scrapertools.downloadpageGzip(item.url)
    if item.extra != "cat":
        data = scrapertools.get_match(data,'</span>  Videos porno gratis más nuevos</h2>(.*?)<div class="publis-bottom">')
    itemlist = []

    patron = '<img src="([^"]+)".*?alt="([^"]+)".*?<h2><a href="([^"]+)">.*?<div class="duracion"><span class="ico-duracion sprite"></span> ([^"]+) min</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for thumbnail, title, url, time in matches:

        scrapedtitle = "" + time + " - " + title
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = thumbnail
        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="play" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle))

    # # EXTRAE EL PAGINADOR
    patronvideos  = '<div class="paginacion">.*?<span class="selected">.*?<a href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    for url, title in matches:
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedtitle = "Página " + title
        if item.extra != "cat":
            itemlist.append( Item(channel=__channel__, action="videos", title=scrapedtitle , url=scrapedurl, folder=True) )
        else:
            itemlist.append( Item(channel=__channel__, action="videos", title=scrapedtitle , url=scrapedurl, extra= "cat", folder=True) )
    return itemlist

def categorias(item):
    logger.info("[canalporno.py] categorias")
    data = scrapertools.downloadpageGzip(item.url)
    data = scrapertools.get_match(data,'<ul class="ordenar-por ordenar-por-categoria">(.*?)<div class="publis-bottom">')
    itemlist = []

    patron = '<div class="muestra-categorias">.*?<a class="thumb" href="([^"]+)".*?<img class="categorias" src="([^"]+)".*?<div class="nombre">([^"]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url, thumbnail, title in matches:

        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = thumbnail
        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="videos" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle, extra="cat", folder=True))

    return itemlist

def play(item):
    logger.info("[canalporno.py] play")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = data.replace("\t", "")
    data = data.replace("\n", "")
    logger.debug(data)

    patron = "playlist:.*?\}.*?url: '([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        scrapedurl = url
        logger.debug("url="+url)
        itemlist.append( Item(channel=__channel__, action="play" , title=item.title, fulltitle=item.fulltitle , url=scrapedurl, thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))
	
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True

    # mainlist
    mainlist_itemlist = mainlist(Item())
    video_itemlist = videos(mainlist_itemlist[0])
    
    # Si algún video es reproducible, el canal funciona
    for video_item in video_itemlist:
        play_itemlist = play(video_item)

        if len(play_itemlist)>0:
            return True

    return False