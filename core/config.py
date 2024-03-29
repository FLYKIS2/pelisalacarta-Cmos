# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# Parámetros de configuración (kodi)
#------------------------------------------------------------

import os

import xbmc
import xbmcaddon

PLATFORM_NAME = "kodi-helix"

PLUGIN_NAME = "pelisalacarta"
__settings__ = xbmcaddon.Addon(id="plugin.video."+PLUGIN_NAME)
__language__ = __settings__.getLocalizedString

def get_platform():
    return PLATFORM_NAME

def is_xbmc():
    return True

def get_library_support():
    return True

def get_system_platform():
    """ fonction: pour recuperer la platform que xbmc tourne """
    import xbmc
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    return platform

def open_settings():
    __settings__.openSettings()

  
def get_setting(name, channel=""):
    """Retorna el valor de configuracion del parametro solicitado.

    Devuelve el valor del parametro 'name' en la configuracion global o en la configuracion propia del canal 'channel'.
    
    Si se especifica el nombre del canal busca en la ruta \addon_data\plugin.video.pelisalacarta\settings_channels el archivo channel_data.json
    y lee el valor del parametro 'name'. Si el archivo channel_data.json no existe busca en la carpeta channels el archivo 
    channel.xml y crea un archivo channel_data.json antes de retornar el valor solicitado.
    Si el parametro 'name' no existe en channel_data.json lo busca en la configuracion global y si ahi tampoco existe devuelve un str vacio.
    
    Parametros:
    name -- nombre del parametro
    channel [opcional] -- nombre del canal
      
    Retorna:
    value -- El valor del parametro 'name'
    
    """   
    if channel:
      from core import channeltools
      value = channeltools.get_channel_setting(name, channel)
      if not value is None:
        return value

    # Devolvemos el valor del parametro global 'name'        
    return __settings__.getSetting( name ) 

def set_setting(name,value, channel=""):
    """Fija el valor de configuracion del parametro indicado.

    Establece 'value' como el valor del parametro 'name' en la configuracion global o en la configuracion propia del canal 'channel'.
    Devuelve el valor cambiado o None si la asignacion no se ha podido completar.
    
    Si se especifica el nombre del canal busca en la ruta \addon_data\plugin.video.pelisalacarta\settings_channels el archivo channel_data.json
    y establece el parametro 'name' al valor indicado por 'value'. Si el archivo channel_data.json no existe busca en la carpeta channels el archivo 
    channel.xml y crea un archivo channel_data.json antes de modificar el parametro 'name'.
    Si el parametro 'name' no existe lo añade, con su valor, al archivo correspondiente.
    
    
    Parametros:
    name -- nombre del parametro
    value -- valor del parametro
    channel [opcional] -- nombre del canal
    
    Retorna:
    'value' en caso de que se haya podido fijar el valor y None en caso contrario
        
    """ 
    if channel:
      from core import channeltools
      return channeltools.set_channel_setting(name,value, channel)
    else:
      try:
          __settings__.setSetting(name,value)
      except:
          logger.info("[config.py] ERROR al fijar el parametro global {0}= {1}".format(name, value))
          return None
              
      return value

    
def get_localized_string(code):
    dev = __language__(code)

    try:
        dev = dev.encode("utf-8")
    except:
        pass
    
    return dev

def get_library_path():

    if get_system_platform() == "xbox":
        default = xbmc.translatePath(os.path.join(get_runtime_path(),"library"))
    else:
        default = xbmc.translatePath("special://profile/addon_data/plugin.video."+PLUGIN_NAME+"/library")

    value = get_setting("librarypath")
    if value=="":
        value=default

    return value

def get_temp_file(filename):
    return xbmc.translatePath( os.path.join( "special://temp/", filename ))

def get_runtime_path():
    return xbmc.translatePath( __settings__.getAddonInfo('Path') )

def get_data_path():
    dev = xbmc.translatePath( __settings__.getAddonInfo('Profile') )
    
    # Parche para XBMC4XBOX
    if not os.path.exists(dev):
        os.makedirs(dev)
    
    return dev

def get_cookie_data():
    import os
    ficherocookies = os.path.join( get_data_path(), 'cookies.dat' )

    cookiedatafile = open(ficherocookies,'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close();

    return cookiedata

# Test if all the required directories are created
def verify_directories_created():
    import logger
    logger.info("pelisalacarta.core.config.verify_directories_created")

    # Force download path if empty
    download_path = get_setting("downloadpath")
    if download_path=="":
        download_path = os.path.join( get_data_path() , "downloads")
        set_setting("downloadpath" , download_path)

    # Force download list path if empty
    download_list_path = get_setting("downloadlistpath")
    if download_list_path=="":
        download_list_path = os.path.join( get_data_path() , "downloads" , "list")
        set_setting("downloadlistpath" , download_list_path)

    # Force bookmark path if empty
    bookmark_path = get_setting("bookmarkpath")
    if bookmark_path=="":
        bookmark_path = os.path.join( get_data_path() , "bookmarks")
        set_setting("bookmarkpath" , bookmark_path)

    # Create data_path if not exists
    if not os.path.exists(get_data_path()):
        logger.debug("Creating data_path "+get_data_path())
        try:
            os.mkdir(get_data_path())
        except:
            pass

    # Create download_path if not exists
    if not download_path.lower().startswith("smb") and not os.path.exists(download_path):
        logger.debug("Creating download_path "+download_path)
        try:
            os.mkdir(download_path)
        except:
            pass

    # Create download_list_path if not exists
    if not download_list_path.lower().startswith("smb") and not os.path.exists(download_list_path):
        logger.debug("Creating download_list_path "+download_list_path)
        try:
            os.mkdir(download_list_path)
        except:
            pass

    # Create bookmark_path if not exists
    if not bookmark_path.lower().startswith("smb") and not os.path.exists(bookmark_path):
        logger.debug("Creating bookmark_path "+bookmark_path)
        try:
            os.mkdir(bookmark_path)
        except:
            pass

    # Create library_path if not exists
    if not get_library_path().lower().startswith("smb") and not os.path.exists(get_library_path()):
        logger.debug("Creating library_path "+get_library_path())
        try:
            os.mkdir(get_library_path())
        except:
            pass

    # Create settings_path is not exists
    settings_path= os.path.join(get_data_path(),"settings_channels")
    if not os.path.exists(settings_path):
        logger.debug("Creating settings_path "+settings_path)
        try:
            os.mkdir(settings_path)
        except:
            pass  

    
    # Checks that a directory "xbmc" is not present on platformcode
    old_xbmc_directory = os.path.join( get_runtime_path() , "platformcode" , "xbmc" )
    if os.path.exists( old_xbmc_directory ):
        logger.debug("Removing old platformcode.xbmc directory")
        try:
            import shutil
            shutil.rmtree(old_xbmc_directory)
        except:
            pass
