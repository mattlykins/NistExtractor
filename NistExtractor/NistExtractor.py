#!/usr/bin/python

import urllib.request
import urllib.parse
import re
import sys
import datetime
import fractions
import os

NIST_LEVEL_SERVER = "http://physics.nist.gov/cgi-bin/ASD/energy1.pl"
NIST_LINE_SERVER = "http://physics.nist.gov/cgi-bin/ASD/lines1.pl"
DEBUGMODE = False
num_level_limit = 1000
unique_nrg_factor = 1e-3
default_species = "Fe_X"


#Convert Roman numeral to integer
def roman_to_int(n):
    numeral_map = zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I'))

    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result

# Test whether a string can be a number
def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
# Remove brackets and punctuation from strings
def remove_junk(string):
    
    #Brackets indicate that the level comes from extrapolation or interpolation
    newstring = string.replace('[','').replace(']','')
    #Parenthesis indicate that the level is theoretical
    newstring = newstring.replace('(','').replace(')','')
    #+x +y etc. indicates that the level has no connection to other levels
    newstring = newstring.replace('+x','').replace('+y','').replace('+z','').replace('+k','')
    #? (and possibly dagger) indicate some uncertianty in the level
    newstring = newstring.replace('?','').replace('&dagger;','')
    # a indicates substantial autoionization broadening
    newstring = newstring.replace('a','')
    return newstring

# Convert energies to indicies
# Input list of energies to convert, list of reference energies, list of reference indices
# Returns list of indices
def energies2indices(nrg,lineg,ref_nrg,ref_dex,ref_g):
    ndex = []
    for x,lg in zip(nrg,lineg):
        if(DEBUGMODE):
            print("Looking for energy = %f and g = %i" % (x,lg))
        match_found = False
        for refnrg,refx,refg in zip(ref_nrg,ref_dex,ref_g):
            if (DEBUGMODE):
                print(refg,lg,refnrg,x)
            if refg == lg and (abs(x-refnrg) <= 2*unique_nrg_factor):
                ndex.append(refx)
                match_found = True
                break
    
        if match_found == False:
            print ("PROBLEM: No energy level match found for %f" % x)
            sys.exit(2)
            
    return ndex

# Query the data from the NIST servers
def getNistData(url,values):
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
    request = urllib.request.Request(url, data)
    response = urllib.request.urlopen(request)
    page = response.read().decode('utf-8')
    #print (level_page)
    table = re.compile('<PRE>(.*?)</PRE>', re.DOTALL | re.IGNORECASE).findall(page)
    return table[0].split('\n')




if len(sys.argv) >= 3:
    species = str(sys.argv[1])
    num_level_limit = (sys.argv[2])
elif len(sys.argv) == 2:
    species = str(sys.argv[1])
else:    
    print("Running default species of %s.\n" % default_species)
    #sys.exit(99)
    species = default_species


# Generate output filenames from the inputs
species_name = species
species = species.replace('_', ' ' )

element_name = species_name.split('_')[0]
ion_numeral = species_name.split('_')[1]
ion_int = roman_to_int(ion_numeral)

base_name = element_name + '_' + str(ion_int)

base_path = element_name.lower() + "/" + base_name.lower() + "/"

base_name = base_name.lower()


if not os.path.exists(base_path):
    os.makedirs(base_path)


energy_output_name = base_path + base_name + ".nrg"
tp_output_name = base_path + base_name + ".tp"


print ("%s data is being saved to %s and %s" % (species,energy_output_name,tp_output_name))

"""
Get the energy level data 
"""
level_values = {'spectrum' : species,
          'format' : '1',
          'units' : '0',
          'multiplet_ordered' : '1',
          'conf_out' : '1',
          'term_out' : '1',
          'level_out' : '1',
          'j_out' : '1',
          'remove_js' : '1' }


try:
    nrgData = getNistData(NIST_LEVEL_SERVER,level_values)
except:
    print ("Could not get level data from NIST given these query values:%s" % level_values)
    exit(2)


#energy_output = open(energy_output_name,"w")
#for ndex in nrgData:
#    energy_output.write(ndex+"\n")
    

#energy_output.close()
    
      
energy = []
configuration = []
term = []
statwt = []
J = []
old_config = ""
old_term = ""

for current_line in nrgData:
    #print(current_line)
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


#for nrg in energy:
    #print (nrg)
    
#Keep track of the modified energies
mod_energies = {}
for i in range(len(energy)):
    if i != (len(energy)-1):
        if( energy[i]/energy[i+1] == 1):
            energy[i+1] = energy[i+1] + unique_nrg_factor
            mod_energies[energy[i]] = energy[i+1]
            #print(energy[i],energy[i+1])

#print (mod_energies)
#print (len(mod_energies))

#Create index list
index = range(1,len(energy)+1)

energy_output = open(energy_output_name,"w")

#Write out the magic number at the top of the file
energy_output.write("11 10 14\n")

for ndex,nrg,stwt,cfg,trm in zip(index,energy,statwt,configuration,term):
    energy_output.write("%i\t%.3f\t%i\t%s\t%s\n" % (ndex,nrg,stwt,cfg,trm))
    if(ndex == int(num_level_limit)):
        energy_output.write("*******************\n")


# Write out End of Data delimiter and NIST Reference including the current date
energy_output.write("**************\n#Reference:\n#NIST  ")
date_today = datetime.date.today()
energy_output.write(date_today.strftime("%Y-%m-%d"))

energy_output.close()  
    
    
    
#**************************************************#
#**************************************************#



#Get the transition data 
line_values = {'spectra' : species,
          'allowed_out' : '1',
          'forbid_out' : '1',
          'format' : '1',
          'units' : '0',
          'line_out' : '1',
          'enrg_out' : '1',
          'g_out' : '1',
          'remove_js' : '1' }

try:
    lineData = getNistData(NIST_LINE_SERVER,line_values)
except:
    print ("Could not get line data from NIST given these query values:%s" % line_values)
    print("This could mean that NIST has no transition data for %s." % species)
    exit(2)


if( DEBUGMODE ):
    for ndex in lineData:
        print(ndex)

line_list = []
eina = []
nrglo = []
nrghi = []
gLo = []
gHi = []
ttype = []
ndexlo = []
ndexhi = []
for current_line in lineData:
    line_list = current_line.split('|')
    temp_eina = line_list[0].strip()
    # Only process lines that have a number for the Einstein A
    if is_number(temp_eina) == True :
        eina.append(float(temp_eina))
        # Energies list item comes out of the first split containing both energies separated
        # by a "-". Split them based on "-" and strip away the whitespaces. 
        try:       
            temp_nrglo = (line_list[2].split('-'))[0].strip()
            temp_nrghi = (line_list[2].split('-'))[1].strip()
        except:
            print("Skipping %s line:%s" % (species,line_list))
            continue
        try:
            nrglo.append(float(remove_junk(temp_nrglo)))
            nrghi.append(float(remove_junk(temp_nrghi)))
        except:
            print ("PROBLEM: Cannot convert energy levels to floats in tp file")
            print ("nrglo = %s\tnrghi = %s\n" % (temp_nrglo,temp_nrghi))
            sys.exit(1)
            
            
        tempgLo = (line_list[3].split('-'))[0].strip()
        tempgHi = (line_list[3].split('-'))[1].strip()
        #print (tempgLo,tempgHi)
        
        gLo.append(float(remove_junk(tempgLo)))
        gHi.append(float(remove_junk(tempgHi)))
        ttype.append(line_list[4].strip())
       
#Match energy levels to indices
ndexlo = energies2indices(nrglo,gLo,energy,index,statwt)
ndexhi = energies2indices(nrghi,gHi,energy,index,statwt)

tp_output = open(tp_output_name,"w")
tp_output.write("11 10 14\n")

for x,y,z,t in zip(ndexlo,ndexhi,eina,ttype):
    tp_output.write("A\t%i\t%i\t%.2e\t%s\n" % (x,y,z,t))
    
tp_output.write("**************\n#Reference:\n#NIST  ")
tp_output.write(date_today.strftime("%Y-%m-%d"))
    
    
tp_output.close() 

sys.exit(0)
