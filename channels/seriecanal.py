# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para seriecanal
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "seriecanal"
__category__ = "S"
__type__ = "generic"
__title__ = "Seriecanal"
__language__ = "ES"

DEBUG = config.get_setting("debug")
URL_BASE = "http://www.seriecanal.com/"


def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.seriecanal mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="series" , title="Últimos episodios" , folder=True))
    itemlist.append( Item(channel=__channel__, action="genero"    , title="Series por género" , folder=True))
    itemlist.append( Item(channel=__channel__, action="alfabetico"    , title="Series por orden alfabético" , folder=True))
    itemlist.append( Item(channel=__channel__, action="search"        , title="Buscar..."))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.seriecanal search")
    item.url="http://www.seriecanal.com/index.php?page=portada&do=category&method=post&category_id=0&order=C_Create&view=thumb&pgs=1&p2=1"
    
    post = "keyserie="+texto 
    item.extra = post
    itemlist = series(item)
    return itemlist

def genero(item):
    logger.info("pelisalacarta.channels.seriecanal genero")
    itemlist = []
    data = scrapertools.cachePage(URL_BASE)
    data = scrapertools.get_match(data, '<ul class="tag-cloud">(.*?)</ul>')
    patron = '<a.*?href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(URL_BASE, scrapedurl)
        itemlist.append(Item(channel=__channel__, action="series", title=scrapedtitle , url=url, folder=True))
    return itemlist

def alfabetico(item):
    logger.info("pelisalacarta.channels.seriecanal alfabetico")
    itemlist = []
    data = scrapertools.cachePage(URL_BASE)
    data = scrapertools.get_match(data, '<ul class="pagination pagination-sm" style="margin:5px 0;">(.*?)</ul>')
    patron = '<a.*?href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(URL_BASE, scrapedurl)
        itemlist.append(Item(channel=__channel__, action="series", title=scrapedtitle , url=url, folder=True))
    return itemlist
	
def series(item):
    logger.info("pelisalacarta.channels.seriecanal series")
    itemlist = []

    if item.extra != "":
        data = scrapertools.cachePage(item.url, post=item.extra)
    else:
        data = scrapertools.cachePage(item.url)
    data = scrapertools.decodeHtmlentities(data)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)

    patron  = '<div class="item-inner" style="margin: 0 20px 0px 0\;"><img src="([^"]+)".*?'
    patron += 'href="([^"]+)" title="Click para Acceder a la Ficha\|([^"]+)">.*?'
    patron += '<strong>([^"]+)</strong></a>.*?'
    patron += '<strong>([^"]+)</strong></p>.*?'
    patron += '<p class="text-warning".*?\;">(.*?)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl, scrapedplot, scrapedtitle, scrapedtemp, scrapedepi in matches:
        title = scrapedtitle+" - "+scrapedtemp+" - "+scrapedepi
        url = urlparse.urljoin(URL_BASE,scrapedurl)

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True))

	#Extra marca siguiente página
    patron_next = '<ul class="pagination pagination-lg">.*?title="Página Actual">.*?<li(.*?)><a href="([^"]+)">([^"]+)</a>'
    match = scrapertools.find_single_match(data, patron_next)
    if len(match)>0:
        if match[0] == "":
            url = urlparse.urljoin(URL_BASE,match[1])
            title = "Página "+match[2]
            itemlist.append( Item(channel=__channel__, action="series", title=title , url=url , folder=True) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.seriecanal findvideos")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = scrapertools.decodeHtmlentities(data)
    #Busca en la seccion descarga/torrent
    data_download = scrapertools.get_match(data, '<th>Enlaces de Descarga mediante P2P o DD</th>(.*?)</table>')
    patron  = '<p class="item_name"><a href="([^"]+)".*?">([^"]+)</a>'
    patron += '[^=]+.*?<a.*?">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data_download)
    scrapertools.printMatches(matches)
    for scrapedurl, scrapedepi, scrapedname in matches:
        scrapedtitle = " - Episodio "+scrapedepi+" - "+scrapedname
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        if scrapedurl.find("magnet") != -1:
            itemlist.append( Item(channel=__channel__, action="play" , title="[Torrent]" + scrapedtitle, url=scrapedurl, extra="torrent"))
        else:
            itemlist.append(servertools.find_video_items(data=scrapedurl))
            for videoitem in itemlist:
                videoitem.channel=__channel__
                videoitem.action="play"
                videoitem.folder=False
                videoitem.title = "["+videoitem.server+"]" + scrapedtitle

    #Busca en la seccion online
    data_online = scrapertools.get_match(data, '<th>Enlaces de Visionado Online</th>(.*?)</table>')
    patron  = '<a href="([^"]+)\\n.*?src="([^"]+)".*?'
    patron += 'title="Enlace de Visionado Online">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data_online)
    scrapertools.printMatches(matches)
    videolist = []
    for scrapedurl, scrapedthumb, scrapedtitle in matches:
        #Deshecha enlaces de trailers
        if scrapedthumb != "images/series/youtube.png":
            #Extrae url de enlace bit.ly
            url = scrapertools.getLocationHeaderFromResponse(scrapedurl)
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            videolist = servertools.find_video_items(data=url)
            for videoitem in videolist:
                videoitem.channel=__channel__
                videoitem.action="play"
                videoitem.folder=False
                videoitem.title = "["+videoitem.server+"]" + " - " + scrapedtitle
                itemlist.append( Item(channel=__channel__, action="play" , extra=videoitem.server, title=videoitem.title, url=videoitem.url))				

    data_temp = scrapertools.get_match(data, '<div class="panel panel-success">(.*?)</table>')
    data_temp = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data_temp)
    data_notemp = scrapertools.find_single_match(data_temp, '<td colspan="7"(.*?)</table>')
    #Comprueba si hay otras temporadas
    if len(data_notemp) == 0:
        patron  = '<tr><td><p class="item_name"><a href="([^"]+)".*?'
        patron += '<p class="text-success"><strong>([^"]+)</strong>'
        matches = re.compile(patron,re.DOTALL).findall(data_temp)
        scrapertools.printMatches(matches)
        for scrapedurl, scrapedtitle in matches:
            url = urlparse.urljoin(URL_BASE, scrapedurl)
            itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=url , folder=True))

    return itemlist

def play(item):
    logger.info("pelisalacarta.channels.seriecanal play")
    itemlist = []
    if item.extra == "torrent":
        itemlist.append( Item(channel=__channel__, action="play" , server="torrent", title=item.title, url=item.url))
    else:
        itemlist.append( Item(channel=__channel__, action="play" , server=item.extra, title=item.title, url=item.url))

    return itemlist