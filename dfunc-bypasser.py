#!/usr/bin/python2
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--url", help="PHPinfo URL: eg. https://example.com/phpinfo.php")
parser.add_argument("--file", help="PHPinfo localfile path: eg. dir/phpinfo")

args = parser.parse_args()

class colors:
    reset='\033[0m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'

print colors.green + """

                                ,---,     
                                  .'  .' `\   
                                  ,---.'     \  
                                  |   |  .`\  | 
                                  :   : |  '  | 
                                  |   ' '  ;  : 
                                  '   | ;  .  | 
                                  |   | :  |  ' 
                                  '   : | /  ;  
                                  |   | '` ,/   
                                  ;   :  .'     
                                  |   ,.'       
                                  '---'         

""" + "\n\t\t\t" + colors.blue + "authors: " + colors.orange + "__c3rb3ru5__" + ", " + "$_SpyD3r_$" + "\n" + colors.reset

if(args.url):
    url = args.url
    phpinfo = requests.get(url).text

elif(args.file):
    phpinfofile = args.file
    phpinfo = open(phpinfofile,'r').read()

else:
    print parser.print_help()
    exit()

modules = []
inp = []

inp = phpinfo.split('disable_functions</td><td class="v">')[1].split("</")[0].split(',')[:-1]

dangerous_functions = ['pcntl_alarm','pcntl_fork','pcntl_waitpid','pcntl_wait','pcntl_wifexited','pcntl_wifstopped','pcntl_wifsignaled','pcntl_wifcontinued','pcntl_wexitstatus','pcntl_wtermsig','pcntl_wstopsig','pcntl_signal','pcntl_signal_get_handler','pcntl_signal_dispatch','pcntl_get_last_error','pcntl_strerror','pcntl_sigprocmask','pcntl_sigwaitinfo','pcntl_sigtimedwait','pcntl_exec','pcntl_getpriority','pcntl_setpriority','pcntl_async_signals','error_log','system','exec','shell_exec','popen','proc_open','passthru','link','symlink','syslog','ld','mail']

if("mbstring.ini" in phpinfo):
    modules += ['mbstring']
    dangerous_functions += ['mb_send_mail']

if("imap.ini" in phpinfo):
    modules += ['imap']
    dangerous_functions += ['imap_open','imap_mail']

if("libvirt-php.ini" in phpinfo):
    modules += ['libvert']
    dangerous_functions += ['libvirt_connect']

if("gnupg.ini" in phpinfo):
    modules += ['gnupg']
    dangerous_functions += ['gnupg_init']

if("imagick.ini" in phpinfo):
    modules += ['imagick']

exploitable_functions = []

for i in dangerous_functions:
    if i not in inp:
        exploitable_functions.append(i)

if len(exploitable_functions)==0:
    print '\nThe disable_functions seems strong'

else:
    print '\nPlease add the following functions in your disable_functions option: '
    print ','.join(exploitable_functions)

if("imagick" in modules):
    print '\nPHP-imagick module is present. It can be exploited using LD_PRELOAD method\n'

if("PHP-FPM"):
    print "If PHP-FPM is there stream_socket_sendto,stream_socket_client,fsockopen can also be used to be exploit by poisoning the request to the unix socket\n"
