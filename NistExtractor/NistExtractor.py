#!/usr/bin/python

import urllib.request
import urllib.parse
import re

NIST_LEVEL_SERVER = "http://physics.nist.gov/cgi-bin/ASD/energy1.pl"
NIST_LINE_SERVER = "http://physics.nist.gov/cgi-bin/ASD/lines1.pl"
"""
data = {}
data['spectra'] = 'H I'
data['allowed_out'] = '1'
#data['language'] = 'Python'
url_values = urllib.parse.urlencode(data)
print(url_values)  # The order may differ from below.
url = NIST_LINE_SERVER
full_url = url + '?' + url_values
data = urllib.request.urlopen(full_url)
"""

url = NIST_LINE_SERVER
values = {'spectra' : 'Ar I',
          'allowed_out' : '1',
          'forbid_out' : '1',
          'format' : '1',
          'units' : '0',
          'line_out' : '1',
          'enrg_out' : '1',
          'g_out' : '1',
          'remove_js' : '1' }

data = urllib.parse.urlencode(values)
data = data.encode('utf-8') # data should be bytes
req = urllib.request.Request(url, data)
response = urllib.request.urlopen(req)
the_page = response.read().decode('utf-8')
#print(the_page)

m=re.compile('<pre>(.*?)</pre>', re.DOTALL).findall(the_page)
test = m[0].split('\n')
print ("STARTSHERE")
#for ndex in test:
#    print(ndex)
print ("ENDSHERE")


url = NIST_LEVEL_SERVER
values = {'spectrum' : 'Ar I',
          'format' : '1',
          'units' : '0',
          'multiplet_ordered' : '1',
          'conf_out' : '1',
          'term_out' : '1',
          'level_out' : '1',
          'j_out' : '1',
          'remove_js' : '1' }

data = urllib.parse.urlencode(values)
data = data.encode('utf-8') # data should be bytes
req = urllib.request.Request(url, data)
response = urllib.request.urlopen(req)
level_page = response.read().decode('utf-8')
#print (level_page)
n=re.compile('<PRE>(.*?)</PRE>', re.DOTALL).findall(level_page)
test = n[0].split('\n')
print ("STARTSHERE")
for ndex in test:
    print(ndex)
print ("ENDSHERE")






