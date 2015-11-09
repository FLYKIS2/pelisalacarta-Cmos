# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para newpct
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")

__category__ = "A"
__type__ = "generic"
__title__ = "Newpct"
__channel__ = "newpct"
__language__ = "ES"
__creationdate__ = "20130308"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[newpct.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="submenu" , title="Películas", url="http://www.newpct.com/include.inc/load.ajax/load.topbar.php?userName=", extra="Peliculas" ))
    itemlist.append( Item(channel=__channel__, action="submenu" , title="Series"   , url="http://www.newpct.com/include.inc/load.ajax/load.topbar.php?userName=", extra="Series" ))
    itemlist.append( Item(channel=__channel__, action="listado" , title="Anime"   , url="http://www.newpct.com/anime/", extra="" ))
    itemlist.append( Item(channel=__channel__, action="listado" , title="Documentales"   , url="http://www.newpct.com/documentales/", extra="" ))
    itemlist.append( Item(channel=__channel__, action="search"    , title="Buscar" ))
  
    return itemlist

def search(item,texto):
    logger.info("[newpct.py] search")
    texto = texto.replace(" ","+")
    
    item.url = "http://www.newpct.com/buscar-descargas/%s" % (texto)
    try:
        return buscador(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def buscador(item):
    logger.info("[newpct.py] buscador")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    #<td class="center" style="border-bottom:solid 1px cyan;">14-09-14</td><td style="border-bottom:solid 1px cyan;"><strong><a href="http://www.newpct.com/descargar-pelicula/malefica-3d-sbs/" title="M&aacute;s informaci&oacute;n sobre Malefica 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]"> <span class="searchTerm">Malefica</span> 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]</a></strong></td><td class="center" style="border-bottom:solid 1px cyan;">10.9 GB</td><td style="border-bottom:solid 1px cyan;"><a href="http://tumejorserie.com/descargar/index.php?link=torrents/059784.torrent" title="Descargar Malefica 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]"><img src="http://newpct.com/v2/imagenes//buttons/download.png"
    
    patron =  '<td class="center" style="border-bottom:solid 1px cyan;">([^<]+)</td>.*?' #createdate
    patron += '<td class="center" style="border-bottom:solid 1px cyan;">([^<]+)</td>.*?' #info
    patron += '<a href="([^"]+)" '                                                       #url
    patron += 'title="Descargar([^"]+)">'                                                #title
    patron += '<img src="([^"]+)"'                                                       #thumbnail
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedcreatedate, scrapedinfo, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapedtitle + "(Tamaño:" + scrapedinfo + "--" + scrapedcreatedate+")"
        
        
        
        itemlist.append( Item(channel=__channel__, title=scrapedtitle, url=scrapedurl, action="play", server="torrent", thumbnail=scrapedthumbnail, fulltitle=scrapedtitle, folder=True) )
    
    from servers import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel=__channel__
        videoitem.action="play"
        videoitem.folder=False
    
    
    return itemlist

#def play(item):


def submenu(item):
    logger.info("[newpct.py] peliculas")
    itemlist=[]
    
    if item.extra == "Peliculas":
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas DVDRIP-BRRIP Castellano" , url="http://www.newpct.com/peliculas-castellano/peliculas-rip/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas Latino" , url="http://www.newpct.com/peliculas-latino/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Estrenos de Cine Castellano" , url="http://www.newpct.com/peliculas-castellano/estrenos-de-cine/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas Alta Definicion HD" , url="http://www.newpct.com/cine-alta-definicion-hd/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas en 3D HD" , url="http://www.newpct.com/peliculas-en-3d-hd/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas DVDFULL" , url="http://www.newpct.com/peliculas-castellano/peliculas-dvd/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Peliculas V.O.Subtituladas" , url="http://www.newpct.com/peliculas-vo/"))
    else:
		itemlist.append( Item(channel=__channel__, action="listado" , title="HDTV Castellano" , url="http://www.newpct.com/series/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Miniseries Castellano" , url="http://www.newpct.com/miniseries-es/" ))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Series TV - V.O.S.E" , url="http://www.newpct.com/series-vo/"))
		itemlist.append( Item(channel=__channel__, action="listado" , title="Últimos Capítulos HD" , url="http://www.newpct.com/series-alta-definicion-hd/"))
		itemlist.append( Item(channel=__channel__, action="series" , title="Series HD [A-Z]" , url="http://www.newpct.com/index.php?l=torrentListByCategory&subcategory_s=1469&more=listar"))
    return itemlist

def listado(item):
    logger.info("[newpct.py] listado")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    
    '''
    <li>
    <a href='http://www.newpct.com/descargar-pelicula/la-pequena-venecia/'>
    <div class='boxgrid captionb'>
    <img src='http://images.newpct.com/banco_de_imagenes/destacados/038707/la-pequeña-venecia--dvdrip--ac3-5-1-español-castellano--2012-.jpg'  alt='Descargar Peliculas Castellano &raquo; Películas RIP La Pequeña Venecia [DVDrip][AC3 5.1 Español Castellano][2012]' />
    <div class='cover boxcaption'>
    <h3>La Pequeña Venecia </h3>
    <p>Peliculas Castellano<br/>
    Calidad: DVDRIP AC3 5.1<br>
    Tama&ntilde;o: 1.1 GB<br>
    Idioma : Español Castellano
    </p>
    </div>
    </div>
    </a>
    <div id='bot-desc'>
    <div id='tinfo'>
    <a class='youtube' href='#' rel='gx9EKDC0UFQ' title='Ver Trailer' alt='Ver Trailer'>
    <img style='width:25px;' src='http://www.newpct.com/images.inc/images/playm2.gif'></a>
    </div>
    <div id='tdescargar' ><a class='atdescargar' href='http://www.newpct.com/descargar-pelicula/la-pequena-venecia/'>DESCARGAR</a></div>
    </div>
    </li>
    '''
    patron  = "<li[^<]+"
    patron += "<a href='([^']+)'[^<]+"
    patron += "<div class='boxgrid captionb'[^<]+"
    patron += "<img src='([^']+)'[^<]+"
    patron += "<div class='cover boxcaption'[^<]+"
    patron += '<h3>([^<]+)</h3>(.*?)</div>'
    
    matches = re.compile(patron,re.DOTALL).findall(data)    

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")

        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot).strip()
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, viewmode="movie_with_plot"))

    # Página siguiente
    '''
    GET /include.inc/ajax.php/orderCategory.php?type=todo&leter=&sql=SELECT+DISTINCT+++%09%09%09%09%09%09torrentID%2C+++%09%09%09%09%09%09torrentCategoryID%2C+++%09%09%09%09%09%09torrentCategoryIDR%2C+++%09%09%09%09%09%09torrentImageID%2C+++%09%09%09%09%09%09torrentName%2C+++%09%09%09%09%09%09guid%2C+++%09%09%09%09%09%09torrentShortName%2C++%09%09%09%09%09%09torrentLanguage%2C++%09%09%09%09%09%09torrentSize%2C++%09%09%09%09%09%09calidad+as+calidad_%2C++%09%09%09%09%09%09torrentDescription%2C++%09%09%09%09%09%09torrentViews%2C++%09%09%09%09%09%09rating%2C++%09%09%09%09%09%09n_votos%2C++%09%09%09%09%09%09vistas_hoy%2C++%09%09%09%09%09%09vistas_ayer%2C++%09%09%09%09%09%09vistas_semana%2C++%09%09%09%09%09%09vistas_mes++%09%09%09%09++FROM+torrentsFiles+as+t+WHERE++(torrentStatus+%3D+1+OR+torrentStatus+%3D+2)++AND+(torrentCategoryID+IN+(1537%2C+758%2C+1105%2C+760%2C+1225))++++ORDER+BY+torrentDateAdded++DESC++LIMIT+0%2C+50&pag=3&tot=&ban=3&cate=1225 HTTP/1.1
    Host: www.newpct.com
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101 Firefox/19.0
    Accept: */*
    Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    X-Requested-With: XMLHttpRequest
    Referer: http://www.newpct.com/peliculas-castellano/peliculas-rip/
    Cookie: adbooth_popunder=5%7CSat%2C%2009%20Mar%202013%2018%3A23%3A22%20GMT
    Connection: keep-alive
    '''
    
    '''
    function orderCategory(type,leter,pag,other)
    {
        
        
        if(leter=='buscar')
        {
            leter = document.getElementById('word').value;
        }
        if(type=='todo')
        {
            document.getElementById('todo').className = "active_todo";
        }	
        if(type=='letter')
        {
            switch(leter)
            {
                case '09':
                document.getElementById('09').className = "active_num";
                break;
                default:
                document.getElementById(leter).className = "active_a";
                break;
            }
        }
        
        var parametros = {
                    "type" : type,
                    "leter" : leter,
                    "sql" : "SELECT DISTINCT   						torrentID,   						torrentCategoryID,   						torrentCategoryIDR,   						torrentImageID,   						torrentName,   						guid,   						torrentShortName,  						torrentLanguage,  						torrentSize,  						calidad as calidad_,  						torrentDescription,  						torrentViews,  						rating,  						n_votos,  						vistas_hoy,  						vistas_ayer,  						vistas_semana,  						vistas_mes  				  FROM torrentsFiles as t WHERE  (torrentStatus = 1 OR torrentStatus = 2)  AND (torrentCategoryID IN (1537, 758, 1105, 760, 1225))    ORDER BY torrentDateAdded  DESC  LIMIT 0, 50",
                    "pag" : pag,   
                    "tot" : '',
                    "ban" : '3',
                    "other": other,
                    "cate" : '1225'
                    
            };
        //alert(type+leter);
        
        $('#content-category').html('<div style="margin:100px auto;width:100px;height:100px;"><img src="http://www.newpct.com/images.inc/images/ajax-loader.gif"/></div>');
            var page = $(this).attr('data');        
            var dataString = 'page='+page;
            
         $.ajax({
              type: "GET",
              url:   'http://www.newpct.com/include.inc/ajax.php/orderCategory.php',
              data:  parametros,
              success: function(data) {
             
                    //Cargamos finalmente el contenido deseado
                    $('#content-category').fadeIn(1000).html(data);
              }
         });
         
    }
    '''
    if item.extra!="":
        bloque=item.extra
    else:
        bloque = scrapertools.get_match(data,"function orderCategory(.*?)\}\)\;")
    logger.info("bloque="+bloque)
    param_type=scrapertools.get_match(data,"<a href='javascript:;' onclick=\"orderCategory\('([^']+)'[^>]+> >> </a>")
    logger.info("param_type="+param_type)
    param_leter=scrapertools.get_match(data,"<a href='javascript:;' onclick=\"orderCategory\('[^']+','([^']*)'[^>]+> >> </a>")
    logger.info("param_leter="+param_leter)
    param_pag=scrapertools.get_match(data,"<a href='javascript:;' onclick=\"orderCategory\('[^']+','[^']*','([^']+)'[^>]+> >> </a>")
    logger.info("param_pag="+param_pag)
    param_sql=scrapertools.get_match(bloque,'"sql"\s*\:\s*"([^"]+)')
    logger.info("param_sql="+param_sql)
    param_tot=scrapertools.get_match(bloque,"\"tot\"\s*\:\s*'([^']*)'")
    logger.info("param_tot="+param_tot)
    param_ban=scrapertools.get_match(bloque,"\"ban\"\s*\:\s*'([^']+)'")
    logger.info("param_ban="+param_ban)
    param_cate=scrapertools.get_match(bloque,"\"cate\"\s*\:\s*'([^']+)'")
    logger.info("param_cate="+param_cate)
    base_url = scrapertools.get_match(bloque,"url\s*\:\s*'([^']+)'")
    logger.info("base_url="+base_url)
    #http://www.newpct.com/include.inc/ajax.php/orderCategory.php?type=todo&leter=&sql=SELECT+DISTINCT+++%09%09%09%09%09%09torrentID%2C+++%09%09%09%09%09%09torrentCategoryID%2C+++%09%09%09%09%09%09torrentCategoryIDR%2C+++%09%09%09%09%09%09torrentImageID%2C+++%09%09%09%09%09%09torrentName%2C+++%09%09%09%09%09%09guid%2C+++%09%09%09%09%09%09torrentShortName%2C++%09%09%09%09%09%09torrentLanguage%2C++%09%09%09%09%09%09torrentSize%2C++%09%09%09%09%09%09calidad+as+calidad_%2C++%09%09%09%09%09%09torrentDescription%2C++%09%09%09%09%09%09torrentViews%2C++%09%09%09%09%09%09rating%2C++%09%09%09%09%09%09n_votos%2C++%09%09%09%09%09%09vistas_hoy%2C++%09%09%09%09%09%09vistas_ayer%2C++%09%09%09%09%09%09vistas_semana%2C++%09%09%09%09%09%09vistas_mes++%09%09%09%09++FROM+torrentsFiles+as+t+WHERE++(torrentStatus+%3D+1+OR+torrentStatus+%3D+2)++AND+(torrentCategoryID+IN+(1537%2C+758%2C+1105%2C+760%2C+1225))++++ORDER+BY+torrentDateAdded++DESC++LIMIT+0%2C+50&pag=3&tot=&ban=3&cate=1225
    url_next_page = base_url + "?" + urllib.urlencode( { "type":param_type, "leter":param_leter, "sql":param_sql, "pag":param_pag, "tot":param_tot, "ban":param_ban, "cate":param_cate } )
    logger.info("url_next_page="+url_next_page)
    itemlist.append( Item(channel=__channel__, action="listado" , title=">> Página siguiente" , url=url_next_page, extra=bloque))

    return itemlist

	
def series(item):
    logger.info("[newpct.py] series")
    itemlist=[]
    #Lista menú Series de la A-Z
    data = scrapertools.cache_page(item.url)
    patron = '<div id="content-abc">(.*?)<\/div>'
    data = re.compile(patron,re.DOTALL|re.M).findall(data)
    patron = 'id="([^"]+)".*?>([^"]+)<\/a>'
    matches = re.compile(patron,re.DOTALL|re.M).findall(data[0])
    for id, scrapedtitle in matches:
        url_base = "http://www.newpct.com/include.inc/ajax.php/orderCategory.php?type=letter&leter=%s&sql=SELECT+DISTINCT+++%09%09%09%09%09%09torrentID%2C+++%09%09%09%09%09%09torrentCategoryID%2C+++%09%09%09%09%09%09torrentCategoryIDR%2C+++%09%09%09%09%09%09torrentImageID%2C+++%09%09%09%09%09%09torrentName%2C+++%09%09%09%09%09%09guid%2C+++%09%09%09%09%09%09torrentShortName%2C++%09%09%09%09%09%09torrentLanguage%2C++%09%09%09%09%09%09torrentSize%2C++%09%09%09%09%09%09calidad+as+calidad_%2C++%09%09%09%09%09%09torrentDescription%2C++%09%09%09%09%09%09torrentViews%2C++%09%09%09%09%09%09rating%2C++%09%09%09%09%09%09n_votos%2C++%09%09%09%09%09%09vistas_hoy%2C++%09%09%09%09%09%09vistas_ayer%2C++%09%09%09%09%09%09vistas_semana%2C++%09%09%09%09%09%09vistas_mes%2C+%09%09%09%09%09%09imagen++%09%09%09%09++FROM+torrentsFiles+as+t+WHERE++%28torrentStatus+%3D+1+OR+torrentStatus+%3D+2%29++AND+%28torrentCategoryID+IN+%281951%2C+2075%2C+1772%2C+1582%2C+1859%2C+1473%2C+1987%2C+1708%2C+1474%2C+2013%2C+1603%2C+2195%2C+2244%2C+1596%2C+2113%2C+1611%2C+1959%2C+1999%2C+2236%2C+2191%2C+1693%2C+1699%2C+2116%2C+1759%2C+2134%2C+1985%2C+2159%2C+1940%2C+1769%2C+2251%2C+2193%2C+1598%2C+2263%2C+1514%2C+1923%2C+1605%2C+1585%2C+2240%2C+2238%2C+2177%2C+2174%2C+1472%2C+2272%2C+1983%2C+2140%2C+1919%2C+1754%2C+1689%2C+1791%2C+1475%2C+1687%2C+2010%2C+1649%2C+2155%2C+2111%2C+1643%2C+1476%2C+2197%2C+1885%2C+1486%2C+2101%2C+1618%2C+1977%2C+1490%2C+2202%2C+2243%2C+2118%2C+1657%2C+1898%2C+2148%2C+1907%2C+2131%2C+1606%2C+1498%2C+1896%2C+2172%2C+2128%2C+1493%2C+1939%2C+1912%2C+1639%2C+2241%2C+1488%2C+1961%2C+2255%2C+2234%2C+1684%2C+1505%2C+1691%2C+1957%2C+1495%2C+1624%2C+2232%2C+1470%2C+1971%2C+2283%2C+2089%2C+1746%2C+2267%2C+1676%2C+1629%2C+1511%2C+2219%2C+1748%2C+1677%2C+1484%2C+1485%2C+2037%2C+1580%2C+2162%2C+2067%2C+1763%2C+1744%2C+1481%2C+1520%2C+2248%2C+1990%2C+2199%2C+2153%2C+1696%2C+2282%2C+2185%2C+1492%2C+1508%2C+1727%2C+2246%2C+2261%2C+2073%2C+2151%2C+2247%2C+2274%2C+2033%2C+2176%2C+1711%2C+2257%2C+1929%2C+2092%2C+1931%2C+1579%2C+2184%2C+1489%2C+2035%2C+2190%2C+2280%2C+2216%2C+1706%2C+2028%2C+2230%2C+2063%2C+2165%2C+1757%2C+1487%2C+1583%2C+2188%2C+2179%2C+2047%2C+2030%2C+2225%2C+2144%2C+2167%2C+1477%2C+2259%2C+2285%2C+1701%2C+1518%2C+1526%2C+1844%2C+1654%2C+1916%2C+1694%2C+1491%2C+2249%2C+1478%2C+1949%2C+1681%2C+1887%2C+1714%2C+2271%2C+1668%2C+2171%2C+1910%2C+2269%2C+2133%2C+1619%2C+1581%2C+2239%2C+2265%2C+1904%2C+1875%2C+2253%2C+1864%2C+1846%2C+1927%2C+2106%2C+2276%2C+2157%2C+1479%2C+1981%2C+1483%2C+2136%2C+2044%2C+2277%2C+1500%2C+1729%2C+1809%2C+1584%2C+1740%2C+2187%2C+2127%2C+1925%2C+1602%2C+2078%2C+2169%2C+2183%2C+1646%2C+1656%2C+2065%2C+2182%2C+1471%2C+2181%2C+1469%29%29++AND+home_active+%3D+0++++ORDER+BY+torrentDateAdded++DESC++LIMIT+0%2C+50&pag=&tot=&ban=3&cate=1469"
        scrapedurl = url_base.replace("%s", id)
        if id!="todo": itemlist.append( Item(channel=__channel__, action="listaseries" , title=scrapedtitle , url=scrapedurl, folder=True))

    return itemlist
	
def listaseries(item):
    logger.info("[newpct.py] listaseries")
    itemlist=[]

    data = scrapertools.cache_page(item.url)
    patron = "<li>.*?<a href='([^']+)'>.*?<img src='([^']+)'.*?<h3>([^']+)<\/h3>"
    matches = re.compile(patron,re.DOTALL|re.M).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append( Item(channel=__channel__, action="episodios" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, folder=True))

    return itemlist

def episodios(item):
    logger.info("[newpct.py] episodios")
    itemlist=[]
	
    data = scrapertools.cache_page(item.url)
    patron = "<ul style='display:none;'.*?>(.*?)<\/ul>"
    data = re.compile(patron,re.DOTALL|re.M).findall(data)
    patron = "<a href='([^']+)'.*?title='([^']+)'"
    for index in range(len(data)):
            matches = re.compile(patron,re.DOTALL|re.M).findall(data[index])
            for scrapedurl, scrapedtitle in matches:
                itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , url=scrapedurl, thumbnail=item.thumbnail, folder=True))

    return itemlist
	

def findvideos(item):
    logger.info("[newpct.py] findvideos")
    itemlist=[]

    data = scrapertools.cache_page(item.url)

    #<span id='content-torrent'>                    <a href='http://tumejorjuego.com/descargar/index.php?link=descargar/torrent/58591/el-tour-de-los-muppets-bluray-screener-espanol-castellano-line-2014.html' rel='nofollow' id='58591' title='el-tour-de-los-muppets-bluray-screener-espanol-castellano-line-2014' class='external-url' target='_blank'>
    torrent_url = scrapertools.find_single_match(data,"<span id='content-torrent'[^<]+<a href='([^']+)'")
    if torrent_url!="":
        itemlist.append( Item(channel=__channel__, action="play" , title="Torrent" , url=torrent_url, server="torrent"))

    from servers import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel=__channel__
        videoitem.action="play"
        videoitem.folder=False
        videoitem.title = "["+videoitem.server+"]"

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    submenu_items = submenu(mainlist_items[0])
    listado_items = listado(submenu_items[0])
    for listado_item in listado_items:
        play_items = findvideos(listado_item)
        
        if len(play_items)>0:
            return True

    return False