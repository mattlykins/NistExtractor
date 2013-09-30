#!/usr/bin/python

import sys
import subprocess
from sys import platform

if len(sys.argv) != 2:
    print("You did not specify an input file. Running for all species.\n")
    input_file_name = "all_species.txt"
    #sys.exit(99)   
else:
    input_file_name = str(sys.argv[1])

input_file = open(input_file_name,"r")
for current_line in input_file:
        #print (current_line)
        if platform.startswith('win'):
            rcode = subprocess.call(["NistExtractor.py",current_line],shell = True)
        else:
            rcode = subprocess.call(["NistExtractor.py",current_line])
            


input_file.close()
    