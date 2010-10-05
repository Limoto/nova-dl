#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import OptionParser
import urllib, re, os
from xml.dom.minidom import parseString as xml_parseString
from time import sleep

optparser = OptionParser(version="%prog git")
optparser.add_option('-q', '--quality', choices=('low', 'high'), dest='quality', default='high', help='Sets quality to download in')
optparser.add_option('-o', '--output', dest='output', help='Sets target file')
optparser.add_option('-g', '--get-url', action='store_true', dest='geturl', default=False, help='Only print the RTMP URL for use with media players.')
(options, arguments) = optparser.parse_args()

def main():
  serverlist, playlist = get_xmls_from_videopage(arguments[0])
  
  if playlist.documentElement.tagName == "error":
    print "Chyba: " + playlist.getElementsByTagName('message')[0].lastChild.wholeText.strip()
    exit(1)
  
  stream = playlist.getElementsByTagName('item')[0].getAttribute('src')
  server_id = playlist.getElementsByTagName('item')[0].getAttribute('server')
  
  url, type = get_server(serverlist, server_id)
  
  # RTMP
  if type == 'stream':
    if options.quality == 'low':
      url += '?slist=' + stream
    else:
      url += '?slist=' + 'mp4:' + stream
    
    if options.output:
      output = options.output
    else:
      output = os.path.basename(stream) + '.flv'

    if options.geturl:
      print url
    else:
      retval = download_rtmp(url, output)
      if retval == 0:
        print "Download completed without errors"
      else:
        print "Download failed"
      
  
  # HTTP
  elif type == 'progressive':
    print "HTTP downloading not implemented"
  
  

def get_xmls_from_videopage(videopage_url):
  videopage = urllib.urlopen(videopage_url).read()
  
  media_id = re.search(r'var media_id = "(\d+)";', videopage).group(1)
  site_id = re.search(r'var site_id = (\d+);', videopage).group(1)
  
  serverlist = urllib.urlopen("http://tn.nova.cz/bin/player/config.php?media_id=%s&site_id=%s" %(media_id, site_id) ).read()
  playlist = urllib.urlopen("http://tn.nova.cz/bin/player/serve.php?media_id=%s&site_id=%s" %(media_id, site_id) ).read()
  
  return ( xml_parseString(serverlist), xml_parseString(playlist) )

def get_server(serverlist, id):
  for server in serverlist.getElementsByTagName('flvserver'):
    if server.getAttribute('id') == id:
      return ( server.getAttribute('url'), server.getAttribute('type') )
      
  #server nenalezen, použije se primární
  for server in serverlist.getElementsByTagName('flvserver'):
    if server.getAttribute('primary') == "true":
      return ( server.getAttribute('url'), server.getAttribute('type') )

def download_rtmp(url, output):
    return os.system('./rtmpdump --rtmp "%s" --flv "%s"' %(url, output) )

if __name__ == "__main__":
  main()

  
