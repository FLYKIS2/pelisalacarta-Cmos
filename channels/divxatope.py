# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para divxatope
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "divxatope"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "Mejor Torrent"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.divxatope mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="menu" , title="Películas" , url="http://www.divxatope.com/",extra="Peliculas",folder=True))
    itemlist.append( Item(channel=__channel__, action="menu" , title="Series" , url="http://www.divxatope.com",extra="Series",folder=True))
    itemlist.append( Item(channel=__channel__, action="search" , title="Buscar..."))

    return itemlist

def menu(item):
    logger.info("pelisalacarta.channels.divxatope menu")
    itemlist=[]

    data = scrapertools.cache_page(item.url)

    data = scrapertools.find_single_match(data,item.extra+"</a[^<]+<ul(.*?)</ul>")

    patron = "<li><a.*?href='([^']+)'[^>]+>([^<]+)</a></li>"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=__channel__, action="lista", title=bold%title , url=url) )
        itemlist.append( Item(channel=__channel__, action="a_z", title=title + " -- " + teal%bold%"[0-9][A-Z]" , url=url) )

    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.divxatope search")

    if item.url=="":
        item.url="http://www.divxatope.com/buscar/descargas"
    item.extra = "search=%25" + texto

    try:
        return lista(item)
    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def lista(item):
    logger.info("pelisalacarta.channels.divxatope lista")
    itemlist = []

    '''
    <li style="width:136px;height:263px;margin:0px 15px 0px 0px;">
    <a href="http://www.divxatope.com/descargar/374639_ahi-os-quedais-web-screener-r6-español-castellano-2014.html" title="Descargar Ahi Os Quedais Web  en DVD-Screener torrent gratis"><div  class='ribbon-estreno' ></div>                           <img class="torrent-image" src="http://www.divxatope.com/uploads/torrents/images/thumbnails2/6798_ahi--os--quedais.jpg" alt="Descargar Ahi Os Quedais Web  en DVD-Screener torrent gratis" style="width:130px;height:184px;" />
    <h2 style="float:left;width:100%;margin:3px 0px 0px 0px;padding:0px 0px 3px 0px;line-height:12px;font-size:12px;height:23px;border-bottom:solid 1px #C2D6DB;">Ahi Os Quedais Web </h2>
    <strong style="float:left;width:100%;text-align:center;color:#000;margin:0px;padding:3px 0px 0px 0px;font-size:11px;line-height:12px;">DVD-Screener<br>Español Castellano                                                       </strong>
    </a>
    </li>
    '''

    # Descarga la pagina
    if item.extra=="":
        data = scrapertools.cachePage(item.url)
    else:
        data = scrapertools.cachePage(item.url , post=item.extra)

    patron  = '<li [^<]+'
    patron += '<a href="([^"]+)".*?'
    patron += '<img class="[^"]+" src="([^"]+)"[^<]+'
    patron += '<h2[^>]+">([^<]+)</h2[^<]+'
    patron += '<strong[^>]+>(.*?)</strong>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,calidad in matches:
        title = scrapedtitle.strip()+" ("+scrapertools.htmlclean(calidad)+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        action = "findvideos"
        if "divxatope.com/descargar/" not in url:
            action = "episodios"

        itemlist.append( Item(channel=__channel__, action=action, title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    ## Paginación
    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)">Next</a></li>')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="lista", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) , folder=True) )
    else:
        next_page_url = scrapertools.find_single_match(data,'<li><input type="button" class="btn-submit" value="Siguiente" onClick="paginar..(\d+)')
        if next_page_url!="":
            itemlist.append( Item(channel=__channel__, action="lista", title=">> Página siguiente" , url=item.url, extra=item.extra+"&pg="+next_page_url, folder=True) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.divxatope episodios")
    itemlist=[]

    ## Descarga la pagina y elimina saltos de líneas y tabuladores de los datos
    data = re.sub(
        r'\n|\t',
        '',
        scrapertools.cachePage(item.url)
    )

    ## Url y title de los episodios encontrados
    #[....]<div class="chap-desc"><a class="chap-title" href="http://www.divxatope.com/descargar/heroes-reborn---temporada-1--en-hdtv-temp-1-cap-5" title="Heroes Reborn - Temporada 1 [HDTV][Cap.105][Español Castellano]">[....]

    patron = '<div class="chap-desc"><a class="chap-title" href="([^"]+)" title="([^"]+)">'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=item.thumbnail , plot=item.plot , folder=True) )

    ## Paginación
    #[....]<a class='active' href='http://www.divxatope.com/serie/sobrenatural/page/x'>x</a><a  href='http://www.divxatope.com/serie/sobrenatural/page/x+1'>[....]
    next_page_url = scrapertools.find_single_match(data,"<a class='active'[^>]+>\d+</a><a  href='([^']+)'")
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="episodios", title=">> Página siguiente", url=next_page_url, folder=True) )

    return itemlist

def a_z(item):
    logger.info("pelisalacarta.channels.divxatope a_z")
    itemlist=[]

    az = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for l in az:
        itemlist.append( Item( channel=item.channel, action='lista', title=l, url=item.url + "/letter/" + l.lower() ) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.divxatope findvideos")
    itemlist=[]

    # Descarga la pagina
    item.url = item.url.replace("divxatope.com/descargar/","divxatope.com/ver-online/")

    '''
    <div class="box1"><img src='http://www.divxatope.com/uploads/images/gestores/thumbs/1411605666_nowvideo.jpg' width='33' height='33'></div>
    <div class="box2">nowvideo</div>
    <div class="box3">Español Castel</div>
    <div class="box4">DVD-Screene</div>
    <div class="box5"><a href="http://www.nowvideo.ch/video/affd21b283421" rel="nofollow" target="_blank">Ver Online</a></div>
    '''

    # Descarga la pagina
    data = scrapertools.cachePage(item.url)

    link = scrapertools.find_single_match(data,'href="http://tumejorserie.*?url=([^"]+)"')
    if link!="":
        link = urlparse.urljoin("http://www.divxatope.com/",link)
        logger.info("pelisalacarta.channels.divxatope torrent="+link)
        itemlist.append( Item(channel=__channel__, action="play", server="torrent", title="Vídeo en torrent" , fulltitle = item.title, url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    patron  = "<div class=\"box1\"[^<]+<img[^<]+</div[^<]+"
    patron += '<div class="box2">([^<]+)</div[^<]+'
    patron += '<div class="box3">([^<]+)</div[^<]+'
    patron += '<div class="box4">([^<]+)</div[^<]+'
    patron += '<div class="box5">(.*?)</div[^<]+'
    patron += '<div class="box6">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist_ver = []
    itemlist_descargar = []

    for servername,idioma,calidad,scrapedurl,comentarios in matches:
        title = "Mirror en "+servername+" ("+calidad+")"+" ("+idioma+")"
        if comentarios.strip()!="":
            title = title + " ("+comentarios.strip()+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        new_item = Item(channel=__channel__, action="extract_url", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , folder=True)
        if comentarios.startswith("Ver en"):
            itemlist_ver.append( new_item)
        else:
            itemlist_descargar.append( new_item )

    for new_item in itemlist_ver:
        itemlist.append(new_item)
    
    for new_item in itemlist_descargar:
        itemlist.append(new_item)

    if len(itemlist)==0:
        itemlist = servertools.find_video_items(data=data)
        #_proxy = "http://anonymouse.org/cgi-bin/anon-www.cgi/"
        for videoitem in itemlist:
            #if videoitem.server == "allmyvideos":
            #    videoitem.url = _proxy+videoitem.url
            videoitem.title = "Enlace encontrado en "+videoitem.server+" ("+scrapertools.get_filename_from_url(videoitem.url)+")"
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

    return itemlist

def extract_url(item):
    logger.info("pelisalacarta.channels.divxatope extract_url")

    itemlist = servertools.find_video_items(data=item.url)

    #_proxy = "http://anonymouse.org/cgi-bin/anon-www.cgi/"
    for videoitem in itemlist:
        #if videoitem.server == "allmyvideos":
        #    videoitem.url = _proxy+videoitem.url
        videoitem.title = "Enlace encontrado en "+videoitem.server+" ("+scrapertools.get_filename_from_url(videoitem.url)+")"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist    

# Verificaci?n autom?tica de canales: Esta funci?n debe devolver "True" si todo est? ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Da por bueno el canal si alguno de los v?deos de "Novedades" devuelve mirrors
    for mainlist_item in mainlist_items:
        if "DVDRip Castellano" in mainlist_item.title:
            peliculas_items = lista(mainlist_item)
            break
    
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = findvideos(pelicula_item)
        if len(mirrors)>0:
            bien = True
            break

    return bien

try:
    is_xbmc = config.is_xbmc()
except:
    is_xbmc = ( not ( "plex" in config.get_platform() or "mediaserver" in config.get_platform() ) )

if is_xbmc:
    blue = "[COLOR blue]%s[/COLOR]"
    bold = "[B]%s[/B]"
    crlf = "[CR]"
    gold = "[COLOR gold]%s[/COLOR]"
    gray = "[COLOR gray]%s[/COLOR]"
    green = "[COLOR green]%s[/COLOR]"
    orange = "[COLOR orange]%s[/COLOR]"
    red = "[COLOR red]%s[/COLOR]"
    teal = "[COLOR teal]%s[/COLOR]"
    whitesmoke = "[COLOR whitesmoke]%s[/COLOR]"
else:
    blue = '<span style="color: blue">%s</span>'
    bold = "<b>%s</b>"
    crlf = "<br>"
    gold = '<span style="color: gold">%s</span>'
    gray = '<span style="color: gray">%s</span>'
    green = '<span style="color: green">%s</span>'
    orange = '<span style="color: orange">%s</span>'
    red = '<span style="color: red">%s</span>'
    teal = '<span style="color: teal">%s</span>'
    whitesmoke = '<span style="color: whitesmoke">%s</span>'
