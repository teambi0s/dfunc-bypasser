import os
import sys
import re
import subprocess


get_defined_function = os.popen("php -r 'print_r(get_defined_functions()[\'internal\']);'").readlines()

b = get_defined_function[2:-1]
b = map(str.strip, b)

for i in range(len(b)):
   b[i] = re.sub(r'.*> ', '', b[i])

get_defined_function = b	# all PHP functions


# All seeds: string, int, file and boolean
string_seed = "'1/../../../../../../../etc/passwd'"

final_seed = ["'" + str(i)+string_seed[2:] for i in range(-10,11)]


fp = open("a.txt","w+")

for i in get_defined_function:
    process = subprocess.Popen("php -r '" + i + "();'",stderr=subprocess.PIPE,shell=True)
    (output,err) = process.communicate()

    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    print err
    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    try:
        minargs = int(re.findall(r'least .* p', err)[0][6:-2])
        print minargs

        arg_to_send = (string_seed+",")*(10) + string_seed

        cmd = 'php -r "' + i + '(' + arg_to_send + ');"'

        process = subprocess.Popen(cmd,stderr=subprocess.PIPE,shell=True)
        (output,err) = process.communicate()

        maxargs = int(re.findall(r'most \d parameters',err)[0][5:-11])
        print maxargs

    except:
        try:
            exactly = int(re.findall(r'exactly .* param',err)[0][8:-6])
            print exactly

            if(exactly):

                minargs = exactly
                print minargs

                maxargs = exactly
                print maxargs

            else:
                minargs=0
                maxargs=0
        except:
            minargs=0
            maxargs=0

    for j in range(minargs,maxargs+1):
        for k in final_seed:

            args = [k]*j

            arg_to_be_send = ",".join(args)
            # print arg_to_be_send

            cmd = 'php -r "' + i + '(' + arg_to_be_send + ');"'
            # print cmd

            fin_cmd = "strace -f "+ cmd + " 2>&1 | grep execve"
            # print fin_cmd

            out = re.findall(r'execve', ''.join(os.popen(fin_cmd).readlines()[1:]))

            if(len(out)>0):
                print fin_cmd
                fp.write(fin_cmd+"\n")

            else:
                print "Not this one...you fuckkkk"


