#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import OptionParser
import urllib, re, os, thread
from xml.dom.minidom import parseString as xml_parseString
from time import sleep

optparser = OptionParser(version="%prog 20090520")
optparser.add_option('-q', '--quality', choices=('low', 'high'), dest='quality', default='high', help='Sets quality to download in')
optparser.add_option('-o', '--output', dest='output', help='Sets target file')
(options, arguments) = optparser.parse_args()

def main():
  serverlist, playlist = get_xmls_from_videopage(arguments[0])
  
  stream = playlist.getElementsByTagName('item')[0].getAttribute('src')
  server_id = playlist.getElementsByTagName('item')[0].getAttribute('server')
  
  url, type = get_server(serverlist, server_id)
  
  # RTMP
  if type == 'stream':
    swfUrl = 'http://archiv.nova.cz/static/cz/shared/app/MediaCenter_Catchup.swf'
    app = 'vod'
    pageUrl = arguments[0]
    tcUrl = url
    
    if options.quality == 'low':
      playpath = stream
    else:
      playpath = 'mp4:' + stream
    
    if options.output:
      output = options.output
    else:
      output = os.path.basename(stream) + '.flv'
    
    global retval
    retval = None
#    last_size=0
    
#    thread.start_new_thread(download_rtmp, (url, playpath, app, swfUrl, tcUrl, pageUrl, output) )
#    while retval == None:
#      sleep(1)
#      size = os.path.getsize(output)
#      print "Downloaded %s KiB of ? (%s KiB/s)" %( size/1024, (size-last_size)/1024)
#      last_size = size
    download_rtmp(url, playpath, app, swfUrl, tcUrl, pageUrl, output)

    if retval:
      print "Download completed without errors"
    else:
      print "Download failed"
      
  
  # HTTP
  elif type == 'progressive':
    print "HTTP downloading not implemented"
  
  

def get_xmls_from_videopage(videopage_url):
  videopage = urllib.urlopen(videopage_url).read()
  
  media_id = re.search(r'var media_id = "(\d+)";', videopage).group(1)
  site_id = re.search(r'var site_id = "(\d+)";', videopage).group(1)
  
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

def download_rtmp(url, playpath, app, swfUrl, tcUrl, pageUrl, output):
    global retval
    retval = os.system('./rtmpdump --rtmp "%s" --playpath "%s" --app "%s" --swfUrl "%s" --tcUrl "%s" --pageUrl "%s" -o "%s"' %(url, playpath, app, swfUrl, tcUrl, pageUrl, output) )

if __name__ == "__main__":
  main()

  