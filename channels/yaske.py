# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para yaske
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urllib
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


__modo_grafico__ = config.get_setting("modo_grafico", "yaske")
CHANNEL_HEADERS = [
    ['User-Agent', 'Mozilla/5.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', "http://www.yaske.ro/"],
    ['Connection', 'keep-alive']
]


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Novedades"          , action="peliculas",       url="http://www.yaske.ro/"))
    itemlist.append( Item(channel=item.channel, title="Por año"            , action="menu_buscar_contenido",      url="http://www.yaske.ro/", extra="year"))
    itemlist.append( Item(channel=item.channel, title="Por género"         , action="menu_buscar_contenido", url="http://www.yaske.ro/", extra="gender"))
    itemlist.append( Item(channel=item.channel, title="Por calidad"        , action="menu_buscar_contenido",  url="http://www.yaske.ro/", extra="quality"))
    itemlist.append( Item(channel=item.channel, title="Por idioma"         , action="menu_buscar_contenido",    url="http://www.yaske.ro/", extra="language"))
    itemlist.append( Item(channel=item.channel, title="Buscar"             , action="search"))

    return itemlist


def search(item,texto):
    logger.info()
    itemlist = []

    try:
        item.url = "http://www.yaske.ro/custom/?search=%s"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(peliculas(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = "http://www.yaske.ro/"
        elif categoria == 'infantiles':
            item.url = "http://www.yaske.ro/genero/animation"
        else:
            return []

        itemlist = peliculas(item)
        if itemlist[-1].title == ">> Página siguiente":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_HEADERS, host="http://www.yaske.ro/")
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    cookie_value = get_cookie_value()

    # Extrae las entradas
    '''
       <li class="item-movies c8">
        <div class="tooltipyk">
        <a class="image-block" href="http://www.yaske.ro/es/pelicula/0010962/ver-the-walking-dead-7x02-online.html" title="The Walking Dead 7x02">
        <img src="http://www.yaske.cc/upload/images/b59808b9b505c15283159099ff7320c6.jpg" alt="The Walking Dead 7x02" width="140" height="200" />
        </a>
    <span class="tooltipm">
        <img class="callout" src="http://www.yaske.cc/upload/tooltip/callout_black.gif" />
        <div class="moTitulo"><b>Título: </b>The Walking Dead 7x02<br><br></div>
        <div class="moSinopsis"><b>Sinopsis: </b>Array<br><br></div>
        <div class="moYear"><b>Año: </b>2016</div>
        </span>
       </div>
        <ul class="bottombox">
            <li><a href="http://www.yaske.ro/es/pelicula/0010962/ver-the-walking-dead-7x02-online.html" title="The Walking Dead 7x02">
                The Walking Dead 7x02    	</a></li>
            <li>Accion, Thrillers, Terror</li>
            <li><img src='http://www.yaske.ro/theme/01/data/images/flags/en_es.png' title='English SUB Spanish' width='25'/> <img src='http://www.yaske.ro/theme/01/data/images/flags/la_la.png' title='Latino ' width='25'/> <img src='http://www.yaske.ro/theme/01/data/images/flags/es_es.png' title='Spanish ' width='25'/> </li>
            <li>        	<img class="opa3" src="http://storage.ysk.pe/b6b5870914222d773c5b76234978e376.png" height="22" border="0">
            </li>
        </ul>
        <div class="quality">Hd Real 720</div>
        <div class="view"><span>view: 6895</span></div>
    </li>
    '''
    if not item.page:
        item.page = 0
    patron  = '<li class="item-movies.*?<a class="image-block" href="([^"]+)" title="([^"]+)">' \
              '<img src="([^"]+).*?<b>Sinopsis: </b>(.*?)<br><br></div>.*?<b>Año: </b>(\d+).*?' \
              '<ul class="bottombox">.*?<li>(<img.*?)</li>.*?</ul>' \
              '<div class="quality">([^<]+)</div>'
 
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, sinopsis, year, idiomas, calidad in matches[item.page:item.page+20]:
        matchesidiomas = scrapertools.find_multiple_matches(idiomas, "<img src='[^']+' title='([^']+)'")
        idiomas_disponibles = ""
        for idioma in matchesidiomas:
            idioma = idioma .replace("Spanish SUB Spanish", "ESP FORZ").replace("Latino SUB Latino", "LAT FORZ") \
                     .replace("English SUB Spanish", "VOSE").replace("Spanish", "ESP").replace("English", "ENG") \
                     .replace("Latino", "LAT")
            idiomas_disponibles += idioma.strip() + "/"

        if idiomas_disponibles:
            idiomas_disponibles = "["+idiomas_disponibles[:-1]+"]"
        
        trailer = scrapertools.find_single_match(idiomas, '<a href="(https://www.youtube.com[^"]+)"')
        title = scrapertools.decodeHtmlentities(scrapedtitle.strip())
        title = title.replace("&colon;", ":")
        contentTitle = title[:]
        title += " "+idiomas_disponibles+" ["+calidad+"]"
        if "yaske.ro/upload" in scrapedthumbnail:
            scrapedthumbnail += "|User-Agent=%s&Cookie=%s" % (CHANNEL_HEADERS[0][1], cookie_value)
        infoLabels = {'plot': sinopsis, 'year': int(year), 'trailer': trailer}

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                             thumbnail=scrapedthumbnail, fulltitle=contentTitle, viewmode="movie",
                             contentTitle=contentTitle, infoLabels=infoLabels))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass
    # Extrae el paginador
    if item.page == 0 and len(matches) > 20:
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=item.url, page=20))
    else:
        next_url = scrapertools.find_single_match(data, "<a href='([^']+)'>\&raquo\;</a>")
        if next_url:
            scrapedurl = urlparse.urljoin(item.url, next_url)
            itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=scrapedurl, page=0))

    return itemlist


def menu_buscar_contenido(item):
    logger.info()
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_HEADERS, host="http://www.yaske.ro/")
    data = scrapertools.find_single_match(data,'<select name="'+item.extra+'"(.*?)</select>')

    # Extrae las entradas
    matches = scrapertools.find_multiple_matches(data, "<option value='([^']+)'>([^<]+)</option>")    
    for scrapedurl, scrapedtitle in matches:
        url = "http://www.yaske.ro/es/peliculas/custom/?"+item.extra+"="+scrapedurl
        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=url, thumbnail=item.thumbnail))

    return sorted(itemlist, key=lambda i:  i.title.lower())


def findvideos(item):
    logger.info("url="+item.url)
    itemlist = []
    
    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_HEADERS, host="http://www.yaske.ro/")
    if not item.infoLabels["plot"]:
        plot = scrapertools.find_single_match(data, '<meta name="sinopsis" content="([^"]+)"')
        item.infoLabels["plot"] = scrapertools.decodeHtmlentities(scrapertools.htmlclean(plot))

    # Extrae las entradas
    '''
    <tr bgcolor="">
    <td height="32" align="center"><a class="btn btn-mini enlace_link" style="text-decoration:none;" rel="nofollow" target="_blank" title="Ver..." href="http://www.yaske.net/es/reproductor/pelicula/2141/44446/"><i class="icon-play"></i><b>&nbsp; Opcion &nbsp; 04</b></a></td>
    <td align="left"><img src="http://www.google.com/s2/favicons?domain=played.to"/>played</td>
    <td align="center"><img src="http://www.yaske.net/theme/01/data/images/flags/la_la.png" width="21">Lat.</td>
    <td align="center" class="center"><span title="" style="text-transform:capitalize;">hd real 720</span></td>
    <td align="center"><div class="star_rating" title="HD REAL 720 ( 5 de 5 )">
    <ul class="star"><li class="curr" style="width: 100%;"></li></ul>
    </div>
    </td> <td align="center" class="center">2553</td> </tr>
    '''

    matches = scrapertools.find_multiple_matches(data, '<tr bgcolor=(.*?)</tr>')
    for tr in matches:
        try:
            title = scrapertools.find_single_match(tr, '<b>([^<]+)</b>')
            server = scrapertools.find_single_match(tr, '"http\://www.google.com/s2/favicons\?domain.*?>([^<]+)')

            # <td align="center"><img src="http://www.yaske.net/theme/01/data/images/flags/la_la.png" width="19">Lat.</td>
            idioma = scrapertools.find_single_match(tr, '<img src="http://www.yaske.[a-z]+/theme/01/data/images/flags/([a-z_]+).png"[^>]+>[^<]*<')
            subtitulos = scrapertools.find_single_match(tr, '<img src="http://www.yaske.[a-z]+/theme/01/data/images/flags/[^"]+"[^>]+>([^<]*)<')
            calidad = scrapertools.find_single_match(tr, '<td align="center" class="center"[^<]+<span title="[^"]*" style="text-transform.capitalize.">([^<]+)</span></td>')
            
            #<a [....] href="http://api.ysk.pe/noref/?u=< URL Vídeo >">
            scrapedurl = scrapertools.find_single_match(tr, '<a.*?href="([^"]+)"')

            title = title.replace("&nbsp;", "")

            calidad = calidad.capitalize()
            if "es_es" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [ESP] ["+calidad+"]"
            elif "la_la" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [LAT] ["+calidad+"]"
            elif "en_es" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [SUB] ["+calidad+"]"
            elif "en_en" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [ENG] ["+calidad+"]"
            else:
                scrapedtitle = title + " en "+server.strip()+" ["+idioma+" / "+subtitulos+"] ["+calidad+"]"
            scrapedtitle = scrapertools.entityunescape(scrapedtitle).strip()
            server_id = server.replace("streamin", "streaminto").replace("waaw", "netutv").replace("netu", "netutv")
            scrapedthumbnail = "http://media.tvalacarta.info/servers/server_"+server_id+".png"

            logger.info("server="+server+", scrapedurl="+scrapedurl)
            if scrapedurl.startswith("http") and not "olimpo.link" in scrapedurl:
                itemlist.append(Item(channel=item.channel, action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, folder=False, parentContent=item))
        except:
            import traceback
            logger.info("Excepcion: "+traceback.format_exc())

    return itemlist


def play(item):
    logger.info("url=" + item.url)
    itemlist=[]

    # http%3A%2F%2Folo.gg%2Fs%2FcJinsNv1%3Fs%3Dhttp%253A%252F%252Fwww.nowvideo.to%252Fvideo%252F9c8bf2ed9d4fd
    data = urllib.unquote(item.url)
    # http://olo.gg/s/cJinsNv1?s=http%3A%2F%2Fwww.nowvideo.to%2Fvideo%2F9c8bf2ed9d4fd
    newdata = scrapertools.find_single_match(data, 'olo.gg/s/[a-zA-Z0-9]+.s.(.*?)$')
    if newdata:
        data = urllib.unquote(newdata)
        logger.info("url="+data)

    itemlist = servertools.find_video_items(item=item, data=data)
    for newitem in itemlist:
        newitem.fulltitle = item.fulltitle
    
    return itemlist


def get_cookie_value():
    from core import filetools
    cookies = filetools.join(config.get_data_path(), 'cookies', 'yaske.ro.dat')
    cookiedata = filetools.read(cookies)
    cfduid = scrapertools.find_single_match(cookiedata, "yaske.*?__cfduid\s+([A-Za-z0-9\+\=]+)")
    cookie_value = "__cfduid=" + cfduid
    cfclearance = scrapertools.find_single_match(cookiedata, "yaske.*?cf_clearance\s+([A-Za-z0-9\+\=\-]+)")
    if cfclearance:
        cookie_value += "; cf_clearance=" + cfclearance

    return cookie_value
