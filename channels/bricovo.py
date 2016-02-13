# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Bricovo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re, urllib
from core import logger
from core import config
from core import scrapertools
from core.item import Item

__channel__ = "bricovo"
__category__ = "A"
__type__ = "generic"
__title__ = "BricoVO"
__language__ = "ES"

DEBUG = config.get_setting("debug")
DEFAULT_HEADERS = ["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"]

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.bricovo mainlist")
    itemlist = []
    itemlist.append(Item(channel=__channel__, title="Películas" , action="lista", url="http://www.bricovo.com/?s=alphabet:all"))
    itemlist.append(Item(channel=__channel__, title="Series"      , action="entradas", url="http://www.bricovo.com/?s=temporada"))
    itemlist.append(Item(channel=__channel__, title="Buscar..."      , action="search", thumbnail= "http://i.imgur.com/aWCDWtn.png", extra="Buscar"))
    return itemlist

def search(item, texto):
    logger.info("pelisalacarta.channels.bricovo search")
    item.url = "http://www.bricovo.com/?s=" + texto
    if item.extra == "Buscar":
        itemlist = entradas(item)
    else:
        itemlist = busqueda(item)
    if len(itemlist) == 0:
        itemlist.append(Item(channel=__channel__, title="[COLOR sandybrown][B]Búsqueda sin resultado[/B][/COLOR]"))
    return itemlist

def busqueda(item):
    logger.info("pelisalacarta.channels.bricovo busqueda")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    bloque = scrapertools.find_single_match(data, '<div id="NormalBlock"(.*?)<div id="ListBlock"')
    patron = '<article class="item-entry">.*?<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<h2 class="title2">.*?">(.*?)</a>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, thumb, title in matches:
        thumb = thumb.replace("thumb_185_","")
        title = ' '.join(title.split())
        if "– Temporada" in title:
            itemlist.append(Item(channel=__channel__, action="findvideos_series", title=title , fulltitle = title, url=url , thumbnail=thumb , plot="", context = "2", folder=True) )
        else:
            itemlist.append(Item(channel=__channel__, action="findvideos_cine", title=title , fulltitle = title, url=url , thumbnail=thumb , plot="", context = "0", folder=True) )

    return itemlist

def lista(item):
    logger.info("pelisalacarta.channels.bricovo lista")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Estrenos"      , action="entradas"    , url="http://www.bricovo.com/c/estrenos/"))
    itemlist.append( Item(channel=__channel__, title="DVDRip"       , action="entradas"    , url="http://www.bricovo.com/c/dvdrip/"))
    itemlist.append( Item(channel=__channel__, title="HD/Micro HD"         , action="entradas"    , url="http://www.bricovo.com/c/hd/"))
    itemlist.append( Item(channel=__channel__, title="BluRay Rip", action="entradas"    , url="http://www.bricovo.com/c/bluray-rip/"))
    return itemlist

def entradas(item):
    logger.info("pelisalacarta.channels.bricovo entradas")
    itemlist = []
    infolabels = {}
    infolabels['plot']=""
    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    bloque = scrapertools.find_single_match(data, '<div id="NormalBlock"(.*?)<div id="ListBlock"')
    patron = '<article class="item-entry">.*?<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" alt="([^"]+)".*?'
    patron += '<h2 class="title2">.*?">(.*?)</a>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, thumb, title_tmdb, title in matches:
        thumb = thumb.replace("thumb_185_","")
        title = ' '.join(title.split())
        if "– Temporada" in title:
            tipo = "tv"
            year = ""
        else:
            tipo = "movie"
            year = re.search('\((.*)\)', title).group(1)
        try:
            plot, fanart = info(title_tmdb, tipo, year)
        except:
            plot = {}
            plot['infoLabels'] = infolabels
            fanart = ""
            pass
        if tipo == "movie":
            itemlist.append(Item(channel=__channel__, action="findvideos_cine", title=title , fulltitle = title, url=url , thumbnail=thumb , plot=str(plot), fanart= fanart, context = "0", folder=True) )
        else:
            itemlist.append(Item(channel=__channel__, action="findvideos_series", title=title , fulltitle = title_tmdb, url=url , thumbnail=thumb , plot=str(plot), fanart= fanart, context = "2", folder=True) )

    #Paginacion
    patron = "<span class='current'>.*?<a href='([^']+)'.*?>(.*?)</a>"
    matches = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        url = matches[0]
        itemlist.append(Item(channel=__channel__, action="entradas", title="Página "+matches[1] , url=url , folder=True) )

    return itemlist

def findvideos_cine(item):
    logger.info("pelisalacarta.channels.bricovo findvideos_cine")
    itemlist = []
    sinopsis = eval(item.plot)

    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    if sinopsis['infoLabels']['plot'] == "":
        plot = scrapertools.find_single_match(data, '<div class="description" itemprop="text">(.*?)</div>')
        sinopsis['infoLabels']['plot'] = ' '.join(plot.split())
    celdas = scrapertools.find_multiple_matches(data, "<tr>(.*?)</tr>")
    for match in celdas:
        patron = '<span class="title">(.*?)</span>.*?'
        patron += '(?:<a id="file"|<a id="magnet").*?href="([^"]+)".*?'
        if '<a class="btn btn-primary"' in match:
            patron += '<a class="btn btn-primary".*?href="([^"]+)"'
        fichas = scrapertools.find_multiple_matches(match, patron)
        for match2 in fichas:
            title = ' '.join(match2[0].split())
            if match2[0].isspace() or len(title)<5:break
            else:
                title = "[COLOR green][Torrent][/COLOR] "+title
                url = match2[1]
                if len(match2)>2:
                    subtitle = urllib.unquote(match2[2])
                else:
                    subtitle = ""
                    title += " [COLOR red][Sin Subs][/COLOR]"
                itemlist.append(Item(channel=__channel__, action="play", title=title , url=url , thumbnail=item.thumbnail, fanart=item.fanart, plot=str(sinopsis), subtitle=subtitle, extra=item.url, folder=False) )

    return itemlist

def findvideos_series(item):
    logger.info("pelisalacarta.channels.bricovo findvideos_series")
    itemlist = []

    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=item.fulltitle, tipo="tv")
    except:
        pass
    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    celdas = scrapertools.find_multiple_matches(data, "<tr>(.*?)</tr>")
    for match in celdas:
        patron = '<span class="title">(.*?)</span>.*?'
        patron += '(?:<a id="file"|<a id="magnet").*?href="([^"]+)".*?'
        if '<a class="btn btn-primary"' in match:
            patron += '<a class="btn btn-primary".*?href="([^"]+)"'
        fichas = scrapertools.find_multiple_matches(match, patron)
        for match2 in fichas:
            title = ' '.join(match2[0].split())
            if match2[0].isspace() or len(title)<5:break
            else:
                try:
                    season = re.search("Temporada ([0-9]+)",item.title).group(1)
                    episode = re.search("- ([0-9]+)",title).group(1)[-2:]
                    sinopsis, thumb = infoepi(otmdb, season, episode)
                except:
                    sinopsis = item.plot
                    thumb = item.thumbnail
                    pass
                title = "[COLOR green][Torrent][/COLOR] "+title
                url = match2[1]
                if len(match2)>2:
                    subtitle = urllib.unquote(match2[2])
                else:
                    subtitle = ""
                    title += " [COLOR red][Sin Subs][/COLOR]"
                itemlist.append(Item(channel=__channel__, action="play", title=title , url=url , thumbnail=thumb, fanart=item.fanart, plot=str(sinopsis), subtitle=subtitle, extra=item.url, folder=False) )

    return itemlist

def play(item):
    logger.info("pelisalacarta.channels.bricovo play")
    itemlist = []
    sub = ""
    DEFAULT_HEADERS.append( ["Referer",item.extra] )
    DEFAULT_HEADERS.append( ["Host", "www.bricolinks.com"])
    data = scrapertools.cachePage(item.url, headers=DEFAULT_HEADERS)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    enlace = scrapertools.find_single_match(data,'<a class="btn btn-primary btn-small".*?href="([^"]+)"')
    logger.info(enlace)
    if item.subtitle != "":
        datasub = scrapertools.cachePage(item.subtitle, headers=DEFAULT_HEADERS)
        datasub = datasub.replace("\n","").replace("\t", "")
        datasub = scrapertools.decodeHtmlentities(datasub)
        sub = scrapertools.find_single_match(datasub,'<a class="btn btn-primary btn-small".*?href="([^"]+)"')
        try:
            import os
            ficherosubtitulo = os.path.join( config.get_data_path(), 'subtitulo_bricovo.srt' )
            if os.path.exists(ficherosubtitulo):
                try:
                    os.remove(ficherosubtitulo)
                except IOError:
                    logger.info("Error al eliminar el archivo subtitulo.srt "+ficherosubtitulo)
                    raise
        
            data = scrapertools.cache_page(sub)
            fichero = open(ficherosubtitulo,"w")
            fichero.write(data)
            fichero.close()
            sub = ficherosubtitulo
        except:
            logger.info("Error al descargar el subtítulo")
    itemlist.append(Item(channel=__channel__, action="play", title=item.title , server="torrent", url=enlace , subtitle=sub, folder=False) )
    return itemlist

def info(title, type, year=""):
    logger.info("pelisalacarta.bricovo info")
    infolabels = {}
    plot = {}
    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=title, tipo= type, year=year)
        infolabels['plot'] = otmdb.get_sinopsis()
        infolabels['year'] = otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        fanart = otmdb.get_backdrop()
        plot['infoLabels'] = infolabels
        return plot, fanart
    except:
        pass

def infoepi(otmdb, season, episode):
    logger.info("pelisalacarta.bricovo infoepi")
    infolabels = {}
    plot = {}
    try:
        infolabels['season'] = season
        infolabels['episode'] = episode
        episodio = otmdb.get_episodio(infolabels['season'], infolabels['episode'])
        if episodio["episodio_sinopsis"] == "": infolabels['plot'] = otmdb.get_sinopsis()
        else: infolabels['plot'] = episodio["episodio_sinopsis"]
        infolabels['year'] = otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        if episodio["episodio_imagen"] == "": thumbnail = otmdb.get_poster()
        else: thumbnail = episodio["episodio_imagen"]
        plot['infoLabels'] = infolabels
        return plot, thumbnail
    except:
        pass
