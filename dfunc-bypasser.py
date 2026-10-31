#!/usr/bin/env python3
import argparse
import re
import sys

try:
    import requests
except ImportError:
    print("[!] pip3 install requests")
    sys.exit(1)


class colors:
    reset  = '\033[0m'
    red    = '\033[31m'
    green  = '\033[32m'
    orange = '\033[33m'
    blue   = '\033[34m'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",  help="PHPinfo URL: eg. https://example.com/phpinfo.php")
    parser.add_argument("--file", help="PHPinfo localfile path: eg. dir/phpinfo")
    parser.add_argument("--debug", action="store_true", help="Dump the raw response for troubleshooting")
    args = parser.parse_args()

    print(colors.green + r"""
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
""" + "\n\t\t\t" + colors.blue + "authors: " + colors.orange
      + "__c3rb3ru5__" + ", " + "$_SpyD3r_$" + "Lawliet06"  + "\n" + colors.reset)

    # ---------- Récupération de la sortie phpinfo ----------
    if args.url:
        try:
            r = requests.get(args.url, timeout=15, allow_redirects=True)
        except Exception as e:
            print(colors.red + f"[!] Requête impossible : {e}" + colors.reset)
            sys.exit(1)
        if r.status_code != 200:
            print(colors.orange + f"[!] HTTP {r.status_code} — la réponse n'est probablement pas un phpinfo." + colors.reset)
        phpinfo = r.text
    elif args.file:
        phpinfo = open(args.file, 'r', errors='ignore').read()
    else:
        parser.print_help()
        sys.exit(0)

    # ---------- Sanity check : le mot-clé doit exister ----------
    if 'disable_functions' not in phpinfo:
        print(colors.red + "[!] 'disable_functions' absent de la réponse." + colors.reset)
        print(colors.orange + "\nPremiers 500 caractères reçus :\n" + phpinfo[:500] + colors.reset)
        print(colors.orange +
              "\nCauses fréquentes :\n"
              "  - le .phar/.php n'est PAS exécuté par PHP (servi en statique)\n"
              "  - URL erronée / 404 / redirection\n"
              "  - le payload uploadé n'est pas un vrai phpinfo()\n"
              "  - l'upload a échoué (extension / MIME refusés)\n" + colors.reset)
        if args.debug:
            print(colors.blue + "\n--- Réponse brute ---\n" + phpinfo + colors.reset)
        sys.exit(1)

    # ---------- Extraction robuste (guillemets doubles OU simples) ----------
    m = re.search(
        r'disable_functions\s*</td>\s*<td[^>]*class=["\']?v["\']?[^>]*>\s*([^<]*)</td>',
        phpinfo, re.IGNORECASE
    )
    if not m:
        idx = phpinfo.find('disable_functions')
        print(colors.red + "[!] Motif disable_functions trouvé mais valeur illisible. Contexte :" + colors.reset)
        print(phpinfo[idx:idx + 400])
        sys.exit(1)

    raw = m.group(1).strip()
    inp = [f.strip() for f in raw.split(',') if f.strip()]

    # ---------- Fonctions dangereuses ----------
    dangerous_functions = [
        'pcntl_alarm','pcntl_fork','pcntl_waitpid','pcntl_wait','pcntl_wifexited',
        'pcntl_wifstopped','pcntl_wifsignaled','pcntl_wifcontinued','pcntl_wexitstatus',
        'pcntl_wtermsig','pcntl_wstopsig','pcntl_signal','pcntl_signal_get_handler',
        'pcntl_signal_dispatch','pcntl_get_last_error','pcntl_strerror','pcntl_sigprocmask',
        'pcntl_sigwaitinfo','pcntl_sigtimedwait','pcntl_exec','pcntl_getpriority',
        'pcntl_setpriority','pcntl_async_signals','error_log','system','exec',
        'shell_exec','popen','proc_open','passthru','link','symlink','syslog','ld','mail'
    ]

    phpinfo_l = phpinfo.lower()
    modules = []

    if 'mbstring' in phpinfo_l:
        modules.append('mbstring');  dangerous_functions += ['mb_send_mail']
    if 'imap'     in phpinfo_l:
        modules.append('imap');      dangerous_functions += ['imap_open', 'imap_mail']
    if 'libvirt'  in phpinfo_l:
        modules.append('libvirt');   dangerous_functions += ['libvirt_connect']
    if 'gnupg'    in phpinfo_l:
        modules.append('gnupg');     dangerous_functions += ['gnupg_init']
    if 'imagick'  in phpinfo_l:
        modules.append('imagick')

    exploitable = [f for f in dangerous_functions if f not in inp]

    print(colors.blue + f"\n[*] disable_functions contient {len(inp)} entrée(s)." + colors.reset)
    print(colors.blue + f"[*] Modules détectés : {', '.join(modules) or 'aucun'}" + colors.reset)

    if not exploitable:
        print(colors.green + "\nThe disable_functions seems strong" + colors.reset)
    else:
        print(colors.orange + "\nPlease add the following functions in your disable_functions option:" + colors.reset)
        print(','.join(exploitable))

    if 'imagick' in modules:
        print(colors.orange + '\nPHP-imagick module is present. It can be exploited using LD_PRELOAD method\n' + colors.reset)

    if 'php-fpm' in phpinfo_l:
        print(colors.orange +
              "If PHP-FPM is there, stream_socket_sendto / stream_socket_client / fsockopen "
              "can also be used (poison the request to the unix socket).\n" + colors.reset)


if __name__ == '__main__':
    main()
