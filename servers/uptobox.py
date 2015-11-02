# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para uptobox
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[uptobox.py] get_video_url(page_url='%s')" % page_url)

      
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'],['Referer',page_url]]
    
    data = scrapertools.cache_page( page_url , headers=headers )

    # Extrae la URL
    pattern = "<source src='([^']+)' type='([^']+)' data-res='([^']+)'"
    matches = re.compile(pattern, re.DOTALL).findall(data)
    video_urls = []
    for match in matches:
        url = match[0]
        type = match[1]
        quality = match[2]
        video_urls.append([ scrapertools.get_filename_from_url(url)[-4:]+"[uptobox] - "+ type + " - " + quality, url]) 

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://uptobox.com/q7asuktfrh4x
    patronvideos  = 'uptobox.com/([a-z0-9]+)'
    logger.info("[uptobox.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[uptobox]"
        url = "http://uptostream.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'uptobox' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
