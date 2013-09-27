#!/usr/bin/python

import urllib.request
import urllib.parse
import re
import sys
import datetime
import fractions

NIST_LEVEL_SERVER = "http://physics.nist.gov/cgi-bin/ASD/energy1.pl"
NIST_LINE_SERVER = "http://physics.nist.gov/cgi-bin/ASD/lines1.pl"
DEBUGMODE = False

# Test whether a string can be a number
def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
# Remove brackets and punctuation from strings
def remove_junk(string):
    newstring = string.replace('?','').replace('[','').replace(']','').replace('+x','')
    return newstring


def getNistData(url,values):
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
    request = urllib.request.Request(url, data)
    response = urllib.request.urlopen(request)
    page = response.read().decode('utf-8')
    #print (level_page)
    table = re.compile('<PRE>(.*?)</PRE>', re.DOTALL | re.IGNORECASE).findall(page)
    return table[0].split('\n')

"""
Get the energy level data 
"""
level_values = {'spectrum' : 'Ar I',
          'format' : '1',
          'units' : '0',
          'multiplet_ordered' : '1',
          'conf_out' : '1',
          'term_out' : '1',
          'level_out' : '1',
          'j_out' : '1',
          'remove_js' : '1' }


nrgData = getNistData(NIST_LEVEL_SERVER,level_values)
#for ndex in nrgData:
#    print(ndex)
    
    
    
energy = []
configuration = []
term = []
statwt = []
J = []
old_config = ""
old_term = ""

for current_line in nrgData:
    print(current_line)
    if not current_line or current_line[0]=='-':
        continue
    
    line_list = current_line.split('|')
    tempenergy = remove_junk(line_list[3].strip())
    tempJ = remove_junk(line_list[2].strip())
    #Save the potential fractional form of J to add to the term
    saveJ = tempJ
        
    # Deal with J when it is a fraction
    # If J does not appear to be a fraction or number, go to the next line
    if is_number(tempJ) == False:
        try:
            tempJ = float(fractions.Fraction(tempJ))
        except:
            if DEBUGMODE == True:
                print ("Problem: The J between the brackets [%s] does not appear to be a number." % tempJ)
            continue            
            
    # Only process lines that have a number for the energy and J
    if is_number(tempenergy) and is_number(tempJ):        
        tempconfig = line_list[0].strip()                
        # Duplicate missing configuration and term information
        if  tempconfig == "":
            configuration.append(old_config)
        else:
            configuration.append(tempconfig)
            old_config = tempconfig        
        
        tempterm = line_list[1].strip()
        if  tempterm == "":
            term.append(old_term + saveJ)
        else:
            term.append(tempterm + saveJ)
            old_term = tempterm
            
        J.append(float(tempJ))    
        
        statwt.append(2*float(tempJ) + 1)        
        tempenergy = float(tempenergy)
        energy.append(tempenergy)


#Create index list
index = range(1,len(energy)+1)

energy_output = open("test.nrg","w")

#Write out the magic number at the top of the file
energy_output.write("11 10 14\n")

for ndex,nrg,stwt,cfg,trm in zip(index,energy,statwt,configuration,term):
    energy_output.write("%i\t%.3f\t%i\t%s\t%s\n" % (ndex,nrg,stwt,cfg,trm))


# Write out End of Data delimiter and NIST Reference including the current date
energy_output.write("**************\n#Reference:\n#NIST  ")
date_today = datetime.date.today()
energy_output.write(date_today.strftime("%Y-%m-%d"))

energy_output.close()








    
    
    
    




"""
Get the transition data 
"""
line_values = {'spectra' : 'Ar I',
          'allowed_out' : '1',
          'forbid_out' : '1',
          'format' : '1',
          'units' : '0',
          'line_out' : '1',
          'enrg_out' : '1',
          'g_out' : '1',
          'remove_js' : '1' }


#test = getNistData(NIST_LINE_SERVER,line_values)
#for ndex in test:
#    print(ndex)









