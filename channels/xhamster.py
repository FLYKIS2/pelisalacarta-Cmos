# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para xhamster
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por boludiko
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

__channel__ = "xhamster"
__category__ = "F"
__type__ = "generic"
__title__ = "xHamster"
__language__ = "ES"
__adult__ = "true"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[xhamster.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"      , title="Útimos videos" , url="http://es.xhamster.com/"))
    itemlist.append( Item(channel=__channel__, action="listcategorias"    , title="Listado Categorias"))
    itemlist.append( Item(channel=__channel__, action="search"    , title="Buscar", url="http://xhamster.com/search.php?q=%s&qcat=video"))
    return itemlist

# REALMENTE PASA LA DIRECCION DE BUSQUEDA

def search(item,texto):
    logger.info("[xhamster.py] search")
    tecleado = texto.replace( " ", "+" )
    item.url = item.url % tecleado
    return videos(item)

# SECCION ENCARGADA DE BUSCAR

def videos(item):
    logger.info("[xhamster.py] videos")
    data = scrapertools.downloadpageGzip(item.url)
    data = scrapertools.get_match(data,'<div class="boxC videoList clearfix">(.*?)<div id="footer">')
    itemlist = []

    patron = "<div class='vDate'>.*?<\/div><a href='([^']+)'.*?><img src='([^']+)'.*?><img.*?><b>([^']+)</b><u>([^']+)</u>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail,time,title in matches:

        scrapedtitle = "" + time + " - " + title
        scrapedurl = url
        scrapedthumbnail = thumbnail
        scrapedplot = ""
        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="detail" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle, folder=True))
		
    patron2 = "<div class='video'><a href='([^']+)'.*?><img src='([^']+)'.*?><img.*?><b>([^']+)</b><u>([^']+)</u>"
    matches2 = re.compile(patron2,re.DOTALL).findall(data)
    for url,thumbnail,time,title in matches2:

        scrapedtitle = "" + time + " - " + title
        scrapedurl = url
        scrapedthumbnail = thumbnail
        scrapedplot = ""
        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="detail" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle, folder=True))
        
    # # EXTRAE EL PAGINADOR
    # #<a href='search.php?q=sexo&qcat=video&page=3' class='last'>Next</a></td></tr></table></div></td>
    patronvideos  = "<div class='pager'>.*?<span>.*?<a href='([^']+)'>([^']+)<\/a>"
    matchess = re.compile(patronvideos,re.DOTALL).findall(data)
    for match in matchess:
        page = match[1]
        scrapedurl = match[0]
        #scrapertools.printMatches(siguiente)
        itemlist.append( Item(channel=__channel__, action="videos", title= "Página " + page , url=scrapedurl , plot="" , folder=True) )

    return itemlist

# SECCION ENCARGADA DE VOLCAR EL LISTADO DE CATEGORIAS CON EL LINK CORRESPONDIENTE A CADA PAGINA
    
def listcategorias(item):
    logger.info("[xhamster.py] listcategorias")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos" , title="Amateur", url="http://es.xhamster.com/channels/new-amateur-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Anal"  , url="http://es.xhamster.com/channels/new-anal-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Asian"  , url="http://es.xhamster.com/channels/new-asian-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="BBW"  , url="http://es.xhamster.com/channels/new-bbw-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="BDSM"  , url="http://es.xhamster.com/channels/new-bdsm-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Beach"  , url="http://es.xhamster.com/channels/new-beach-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Big Boobs"  , url="http://es.xhamster.com/channels/new-big_boobs-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Bisexuals"  , url="http://es.xhamster.com/channels/new-bisexuals-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Black and Ebony"  , url="http://es.xhamster.com/channels/new-ebony-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Blowjobs"  , url="http://es.xhamster.com/channels/new-blowjobs-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="British"  , url="http://es.xhamster.com/channels/new-british-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Cartoons"  , url="http://es.xhamster.com/channels/new-cartoons-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Celebrities"  , url="http://es.xhamster.com/channels/new-celebs-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Cream Pie"  , url="http://es.xhamster.com/channels/new-creampie-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Cuckold"  , url="http://es.xhamster.com/channels/new-cuckold-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Cumshots"  , url="http://es.xhamster.com/channels/new-cumshots-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Eleccion femenina"  , url="http://es.xhamster.com/channels/new-female_choice-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Female"  , url="http://es.xhamster.com/channels/new-female_choice-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Femdom"  , url="http://es.xhamster.com/channels/new-femdom-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Flashing"  , url="http://es.xhamster.com/channels/new-flashing-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="French"  , url="http://es.xhamster.com/channels/new-french-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="German"  , url="http://es.xhamster.com/channels/new-german-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Grannies"  , url="http://es.xhamster.com/channels/new-grannies-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Group Sex"  , url="http://es.xhamster.com/channels/new-group-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Hairy"  , url="http://es.xhamster.com/channels/new-hairy-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Handjobs"  , url="http://es.xhamster.com/channels/new-handjobs-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Hidden Cam"  , url="http://es.xhamster.com/channels/new-hidden-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Interracial"  , url="http://es.xhamster.com/channels/new-interracial-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Japanese"  , url="http://es.xhamster.com/channels/new-japanese-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Latin"  , url="http://es.xhamster.com/channels/new-latin-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Lesbians"  , url="http://es.xhamster.com/channels/new-lesbians-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Massage"  , url="http://es.xhamster.com/channels/new-massage-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Morenas"  , url="http://es.xhamster.com/channels/new-brunettes-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Masturbation"  , url="http://es.xhamster.com/channels/new-masturbation-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Matures"  , url="http://es.xhamster.com/channels/new-matures-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="MILFs"  , url="http://es.xhamster.com/channels/new-milfs-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Old and Young"  , url="http://es.xhamster.com/channels/new-old_young-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Orgia"  , url="http://es.xhamster.com/channels/new-group-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Public Nudity"  , url="http://es.xhamster.com/channels/new-public-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Sex Toys"  , url="http://es.xhamster.com/channels/new-toys-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Spanish"  , url="http://es.xhamster.com/channels/new-spanish-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Stockings"  , url="http://es.xhamster.com/channels/new-stockings-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Squirting"  , url="http://es.xhamster.com/channels/new-squirting-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Swingers"  , url="http://es.xhamster.com/channels/new-swingers-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Teens"  , url="http://es.xhamster.com/channels/new-teens-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Trios"  , url="http://es.xhamster.com/channels/new-threesomes-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Upskirts"  , url="http://es.xhamster.com/channels/new-upskirts-1.htm"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Vintage"  , url="http://es.xhamster.com/channels/new-vintage-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Videos HD"  , url="http://es.xhamster.com/channels/new-hd_videos-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Voyeur"  , url="http://es.xhamster.com/channels/new-voyeur-1.html"))
    itemlist.append( Item(channel=__channel__, action="videos" , title="Webcams"  , url="http://es.xhamster.com/channels/new-webcams-1.html"))
    return itemlist
    

# OBTIENE LOS ENLACES SEGUN LOS PATRONES DEL VIDEO Y LOS UNE CON EL SERVIDOR
def detail(item):
    logger.info("[xhamster.py] play")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.debug(data)

    patron = 'sources: {"240p":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:

        url = url.replace("\\", "")
        logger.debug("url="+url)
        itemlist.append( Item(channel=__channel__, action="play" , title=item.title + " 240p", fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))
		
    patron = 'sources: {"240p":".*?","480p":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
		for url in matches:

			url = url.replace("\\", "")
			logger.debug("url="+url)
			itemlist.append( Item(channel=__channel__, action="play" , title=item.title + " 480p", fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))

    patron = 'sources: {"240p":".*?","480p":".*?","720p":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
		for url in matches:

			url = url.replace("\\", "")
			logger.debug("url="+url)
			itemlist.append( Item(channel=__channel__, action="play" , title=item.title + " 720p", fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))
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