# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Inkapelis
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "inkapelis"
__category__ = "F"
__type__ = "generic"
__title__ = "Inkapelis"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.inkapelis mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"      , action="peliculas"    , url="http://www.inkapelis.com/"))
    itemlist.append( Item(channel=__channel__, title="Estrenos"       , action="peliculas"   , url="http://www.inkapelis.com/genero/estrenos/"))
    itemlist.append( Item(channel=__channel__, title="Géneros"  , action="generos"   , url="http://www.inkapelis.com/"))
    itemlist.append( Item(channel=__channel__, title="Buscar"  , action="search"   , url="http://www.inkapelis.com/?s="))
    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.inkapelis generos")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<li class="cat-item cat-item-.*?><a href="([^"]+)".*?>([^"]+)<b>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        title =  match[1]
        url = match[0]
        if DEBUG: logger.info("title=["+title+"], url=["+url+"]")
        if (title != "Estrenos ") and (title!= "Próximos Estrenos ") :
            itemlist.append( Item(channel=__channel__, action='peliculas', title=title , url=url , thumbnail="" , folder=True) )

    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.channels.inkapelis peliculas")
    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
	
	#IF en caso de busqueda
    if item.extra == "Buscar":
        # Extrae las entradas
				
		patron ='<div class="col-xs-2">.*?<a href="([^"]+)" title="([^"]+)"> <img src="([^"]+)".*?<p class="text-list">([^"]+)<\/p>'
		matches = re.compile(patron,re.DOTALL).findall(data)

		for match in matches:
			scrapedtitle = match[1]
			scrapedurl = match[0]
			scrapedthumbnail = match[2]
			scrapedplot = scrapertools.htmlclean(match[3])
			if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
			itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
		
		# Extrae la marca de siguiente página
		patron ='<span class="current">.*?<\/span><a href="([^"]+)".*? title="([^"]+)">'
		matches2 = re.compile(patron,re.DOTALL).findall(data)
		for match in matches2:
			url = match[0] 
			title = "Página " + match[1]
			if DEBUG: logger.info("title=["+title+"], url=["+url+"]")
			itemlist.append( Item(channel=__channel__, action='peliculas', title= title , url=url , thumbnail="", extra = "Buscar", folder=True) )

    else:
        # Extrae las entradas
		patron = '<div class="col-mt-5 postsh"><div class="poster-media-card([^"]+)"> <a href="([^"]+)" title="([^"]+)">'
		patron += '<div class=".*?"><\/div><div class=".*?"><\/div><div class="([^"]+)"><\/div>.*?<div class="idiomes">'
		patron += '<div class="([^"]+)"><\/div>.*?<img.*?src="([^"]+)"'
		if (item.extra == "Novedades") or (item.title == "Novedades") :
			data2 = data.split("<h3>Últimas Películas Agregadas</h3>", 1)
			matches = re.compile(patron,re.DOTALL).findall(data2[1])
		else:
			matches = re.compile(patron,re.DOTALL).findall(data)


		for match in matches:
			url = match[1] 
			title = match[2] + " -"+match[0] + " "
			if match[3] == "nuevac": title += "Nueva Calidad - "
			title += match[4]
			thumbnail = match[5]
			if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
			itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail , plot="", folder=True) )

	  # Extrae la marca de siguiente página

		patron ='<span class="current">.*?<\/span><a href="([^"]+)".*? title="([^"]+)">'
		matches2 = re.compile(patron,re.DOTALL).findall(data)
		for match in matches2:
			url = match[0] 
			title = "Página " + match[1]
			if DEBUG: logger.info("title=["+title+"], url=["+url+"]")
			if (item.extra == "Novedades") or (item.title == "Novedades") :
				itemlist.append( Item(channel=__channel__, action='peliculas', title= title , url=url , thumbnail="", extra= "Novedades" ,folder=True) )
			else:
				itemlist.append( Item(channel=__channel__, action='peliculas', title= title , url=url , thumbnail="" ,folder=True) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.inkapelis findvideos")
    
    itemlist = []
    # Descarga la pagina
   
    data = scrapertools.cache_page(item.url)
    
    patronlinks = '<td><a href="([^"]+)".*?title="([^"]+)".*?<td>([^"]+)<\/td><td>([^"]+)<\/td>'
    matches = re.compile(patronlinks,re.DOTALL).findall(data)
    
    for match in matches:
        url = match[0]
        title = match[1] + " - " + match[2] + " - " + match[3]
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=url , thumbnail=item.thumbnail, folder=True) )

    return itemlist

def play(item):
    logger.info("pelisalacarta.inkapelis play")

    media_url = scrapertools.get_header_from_response(item.url,header_to_get="Location")
    itemlist = servertools.find_video_items(data=media_url)

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(data=item.url)
        
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.inkapelis search")
    itemlist = []

    # descarga la pagina
    url = item.url + texto
    data = scrapertools.cache_page(url)
    
    # Extrae las entradas
            
    patron ='<div class="col-xs-2">.*?<a href="([^"]+)" title="([^"]+)"> <img src="([^"]+)".*?<p class="text-list">([^"]+)<\/p>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[0]
        scrapedthumbnail = match[2]
        scrapedplot = scrapertools.htmlclean(match[3])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

  # Extrae la marca de siguiente página

    patron ='<span class="current">.*?<\/span><a href="([^"]+)".*? title="([^"]+)">'
    matches2 = re.compile(patron,re.DOTALL).findall(data)
    for match in matches2:
        url = match[0] 
        title = "Página " + match[1]
        if DEBUG: logger.info("title=["+title+"], url=["+url+"]")
        itemlist.append( Item(channel=__channel__, action='peliculas', title= title , url=url , thumbnail="", extra = "Buscar" , folder=True) )

    return itemlist