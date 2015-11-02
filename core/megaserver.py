# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Megaserver
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import sys
import os
import urllib2
import urllib
import re
from core import logger
import struct
import base64
import json
import random
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time
from core import config
from Crypto.Cipher import AES
from Crypto.Util import Counter


class MEGAServer(object):
  attributes = None
  file = None
  def __init__(self):
    global seqno
    seqno = random.randint(0, 0xFFFFFFFF)
    
  def start(self, puerto):
    server = ThreadedHTTPServer(('', puerto), Handler)
    Thread(target=server.serve_1minute).start()
 
  def get_file_attributes(self, url):

    if len(url.split("!")) ==3:
      file_id = url.split("!")[1]
      file_key = url.split("!")[2]
      self.file = api_req({'a': 'g', 'g': 1, 'p': file_id})

    elif len(url.split("!")) ==4:
      file_id = url.split("!")[1]
      file_key = url.split("!")[2]
      folder_id = url.split("!")[3]
      self.file = api_req({"a":"g","g":1,"n":file_id},"&n="+folder_id)
      
    key = base64_to_a32(file_key)
    k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
    attributes = base64urldecode(self.file['at']) 
    self.attributes = dec_attr(attributes, k)

  
  def get_filename(self, url):
    if self.attributes is None:
      self.get_file_attributes(url)
    return self.attributes['n']
    
  def get_size(self, url):
    if self.attributes is None:
      self.get_file_attributes(url)
    return self.file['s'] 
       
  def get_files(self, url):
    folder_id = url.split("!")[1]
    folder_key = url.split("!")[2]
    master_key = base64_to_a32(folder_key)
    files = api_req({"a":"f","c":1},"&n="+folder_id)
    urls = []
    for file in files["f"]:
      if file["t"] == 0:
        key = file['k'][file['k'].index(':') + 1:]
        key = decrypt_key(base64_to_a32(key), master_key)
        k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
        attributes = base64urldecode(file['a']) 
        attributes = dec_attr(attributes, k)
        
        urls.append({"name": attributes["n"], "url":"!"+file["h"]+"!"+a32_to_base64(key)+"!"+folder_id, "size":file['s']})    
    return urls
    
def base64urldecode(data):
  data += '=='[(2 - len(data) * 3) % 4:]
  for search, replace in (('-', '+'), ('_', '/'), (',', '')):
    data = data.replace(search, replace)
  return base64.b64decode(data)
 
def base64urlencode(data):
  data = base64.b64encode(data)
  for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
    data = data.replace(search, replace)
  return data

def a32_to_str(a):
  return struct.pack('>%dI' % len(a), *a)
 
def str_to_a32(b):
  if len(b) % 4: # Add padding, we need a string with a length multiple of 4
    b += '\0' * (4 - len(b) % 4)
  return struct.unpack('>%dI' % (len(b) / 4), b)
 
def base64_to_a32(s):
  return str_to_a32(base64urldecode(s))
  
def a32_to_base64(a):
  return base64urlencode(a32_to_str(a))
  
def aes_cbc_decrypt(data, key):
  decryptor = AES.new(key, AES.MODE_CBC, '\0' * 16)
  return decryptor.decrypt(data)
 
def aes_cbc_decrypt_a32(data, key):
  return str_to_a32(aes_cbc_decrypt(a32_to_str(data), a32_to_str(key)))

def decrypt_key(a, key):
  return sum((aes_cbc_decrypt_a32(a[i:i+4], key) for i in xrange(0, len(a), 4)), ())

def api_req(req, get=""):
  global seqno
  url = 'https://g.api.mega.co.nz/cs?id=%d%s' % (seqno, get)
  seqno += 1
  return json.loads(post(url, json.dumps([req])))[0]
 
def post(url, data):
  return urllib.urlopen(url, data).read()

def dec_attr(attr, key):
  attr = aes_cbc_decrypt(attr, a32_to_str(key)).rstrip('\0')
  return json.loads(attr[4:]) if attr[:6] == 'MEGA{"' else False

#HTTPServer con timeout
class MyHTTPServer(HTTPServer):  
    Connections = 0
    def handle_error(self, request, client_address):
      import traceback
      if config.get_runtime_path() in traceback.format_exc():
        logger.info(traceback.format_exc()) 
    def serve_1minute(self):
      self.timeout = 30
      x=0
      Thread(target=self.serve_forever).start()
      while x < self.timeout:
            time.sleep(1)
            if self.Connections < 1: 
              x+=1
            else:
              x= 0           
      logger.info( "Servidor detenido (timeout)")
      self.socket.close()
      self.shutdown()
      

      
class Handler(BaseHTTPRequestHandler):
          KeyCache={}
          Peticion={}
          
          Buffer=""
          Conexion = None
          decryptor = None
          
          LeyendoBuffer = False
          EscribiendoBuffer = False
          DescargaTerminada = False
          
          Bloques = 1024*100
          BloquesBuffer = 500
          
          def log_message(self, format, *args): 
            pass
            
          def ChangeUnits(self,value=0):
            Unidades = ["Bytes", "KB", "MB", "GB"]
            Retorno = float(value)
            x=0
            while Retorno >= 1024:
              Retorno = Retorno / 1024
              x+=1
            Unidad = Unidades[x]
            return Retorno, Unidad
          
          def print_message(self):            
            pass
            '''
            os.system('cls' if os.name == 'nt' else 'clear')
            if not self.path in self.KeyCache: 
              print "Primera peticion, Iniciando cache"            
            if "Inicio" in self.Peticion:
              print("Rango: "+ str(self.Peticion["Inicio"]) + "-" + str(self.Peticion["Fin"])+"/"+str(self.KeyCache[self.path]["size"]) )
            if "Leido" in self.Peticion:
              print ""
              print "%.1f%% - Descargando: %.1f%s de %.1f%s" %((float(self.Peticion["Leido"]) *100 / float(self.Peticion["Length"]),) + self.ChangeUnits(self.Peticion["Leido"]) + self.ChangeUnits(self.Peticion["Length"]))
              print "Buffer: %.1f%%" % (float(len(self.Buffer)) * 100 / float(self.BloquesBuffer * self.Bloques))
            if "Escrito" in self.Peticion:
              print "Enviado: %.1f%s" % self.ChangeUnits(self.Peticion["Escrito"])
            '''  
              
          def get_info(self): 
            self.server.Connections +=1
            self.print_message()
            
            if not self.path in self.KeyCache: 
              self.KeyCache[self.path] = {}
              if len(self.path.split("!")) ==3:
                self.KeyCache[self.path]["file_id"] = self.path.split("!")[1]
                self.KeyCache[self.path]["file_key"] =  self.path.split("!")[2]
                self.KeyCache[self.path]["file"] = api_req({'a': 'g', 'g': 1, 'p': self.KeyCache[self.path]["file_id"]})
                
              elif len(self.path.split("!")) ==4:
                self.KeyCache[self.path]["file_id"] = self.path.split("!")[1]
                self.KeyCache[self.path]["file_key"] =  self.path.split("!")[2]
                self.KeyCache[self.path]["folder_id"] =  self.path.split("!")[3]
                self.KeyCache[self.path]["file"] = api_req({"a":"g","g":1,"n":self.KeyCache[self.path]["file_id"]},"&n="+self.KeyCache[self.path]["folder_id"])
                
              self.KeyCache[self.path]["key"] = base64_to_a32(self.KeyCache[self.path]["file_key"])
              self.KeyCache[self.path]["k"] = (self.KeyCache[self.path]["key"][0] ^ self.KeyCache[self.path]["key"][4], self.KeyCache[self.path]["key"][1] ^ self.KeyCache[self.path]["key"][5], self.KeyCache[self.path]["key"][2] ^ self.KeyCache[self.path]["key"][6], self.KeyCache[self.path]["key"][3] ^ self.KeyCache[self.path]["key"][7])
              self.KeyCache[self.path]["iv"] = self.KeyCache[self.path]["key"][4:6] + (0, 0)
              self.KeyCache[self.path]["url"] = self.KeyCache[self.path]["file"]['g']
              self.KeyCache[self.path]["size"] = self.KeyCache[self.path]["file"]['s']
              self.KeyCache[self.path]["attributes"] = base64urldecode(self.KeyCache[self.path]["file"]['at']) 
              self.KeyCache[self.path]["attributes"] = dec_attr(self.KeyCache[self.path]["attributes"], self.KeyCache[self.path]["k"])
              
            if not self.headers.get("range") ==None:
              patron="([0-9]*)-([0-9]*)"
              self.Peticion["Inicio"],self.Peticion["Fin"] = re.compile(patron,re.DOTALL).findall(self.headers.get("range"))[0]
              
            else:
              self.Peticion["Inicio"]= 0
              self.Peticion["Fin"] = ""
              
            self.Peticion["Inicio"] = int(self.Peticion["Inicio"])

            self.print_message()
            self.Peticion["Length"] = self.KeyCache[self.path]["size"] - self.Peticion["Inicio"]
            
          def do_GET(self):   
            self.get_info()
            logger.info("-"*20)
            logger.info("Petición entrante: "+ self.path)
            logger.info("Rango: "+ str(self.Peticion["Inicio"]) + "-" + str(self.Peticion["Fin"])+"/"+str(self.KeyCache[self.path]["size"]) )
            logger.info("-"*20)
            req = urllib2.Request(self.KeyCache[self.path]["url"])
            req.headers['Range'] = 'bytes=%s-%s' % (self.Peticion["Inicio"], self.Peticion["Fin"])
            self.connexion = urllib2.urlopen(req)          
            

            self.send_response(206)
            self.send_header("Content-Range", "bytes " + str(self.Peticion["Inicio"]) +"-"+str(self.Peticion["Fin"])+"/"+str(self.KeyCache[self.path]["size"]) )
            self.send_header("Content-Length", str(self.Peticion["Length"]))
            self.end_headers()
            
            #Decoder
            initial_value = (((self.KeyCache[self.path]["iv"][0] << 32) + self.KeyCache[self.path]["iv"][1]) << 64) + int(self.Peticion["Inicio"]/16)
            Resto =  self.Peticion["Inicio"] - int(self.Peticion["Inicio"]/16)*16
            
            self.decryptor = AES.new(a32_to_str(self.KeyCache[self.path]["k"]), AES.MODE_CTR, counter = Counter.new(128, initial_value = initial_value) )
            if Resto:
              self.decryptor.decrypt(str(0)*Resto)
            
            
            self.Buffer = ""
            self.DescargaTerminada = False
            self.Peticion["Escrito"] = 0
            
            #Se inicia el llenado del bufer 
            Thread(target=self.ReadBuffer).start()
            
            
            #Se inicia el bucle para enviar los datos
            time.sleep(2)
            while True:
              #si el buffer está vacío:
              if len(self.Buffer) ==0:
                #Si la descarga ha terminado, finaliza, sino espera a que se llene
                if not self.DescargaTerminada:
                  continue
                else:
                  break
              enviar = self.Buffer[:self.Bloques]
              self.Buffer= self.Buffer[self.Bloques:]
              self.Peticion["Escrito"] += len(enviar)

              try:
                self.wfile.write(enviar)
              except Exception as e:
                self.connexion.close()
                raise
            self.server.Connections -=1
            self.wfile.close()  
            self.connexion.close()
            
            
          def ReadBuffer(self):
            self.Peticion["Leido"] = 0
            while True:
              if len(self.Buffer)> self.Bloques * self.BloquesBuffer:
                continue
              try:
                chunk = self.connexion.read(self.Bloques)
              except:
                return
              self.Peticion["Leido"] += len(chunk)
              if len(chunk) == 0: break
              chunk = self.decryptor.decrypt(chunk)
              self.print_message()
              self.Buffer += chunk
              if len(chunk) < self.Bloques: break
            self.DescargaTerminada = True 
            self.connexion.close()
                     
class ThreadedHTTPServer(ThreadingMixIn, MyHTTPServer):
  pass
  