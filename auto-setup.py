#!/usr/bin/env python

import yaml
import sys
import os


W = "\033[0m"  # default/white
BLA = "\033[30m"  # black
R = "\033[31m"  # red
G = "\033[32m"  # green
O = "\033[33m"  # orange
BLU = "\033[34m"  # blue
P = "\033[35m"  # purple
C = "\033[36m"  # cyan
GR = "\033[37m"  # gray
BOLD = "\033[1m"
INFO = "%s%s[*]%s " % (BOLD, C, W)
PROMPT = "%s%s[?]%s " % (BOLD, P, W)
ERROR = "%s%s[!]%s " % (BOLD, R, W)

DOCKER = "docker"
DOCKERCOMPOSEFILE = "docker-compose.yml"

NGINX_TEMPALTE = """
server {
    # Redirect HTTP to www
    listen 80;
    server_name fakedomain.com;
    location / {
        rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
    }
}

server {
    # Redirect payloads to HTTPS
    listen 80;
    server_name *.fakedomain.com;
    proxy_set_header X-Forwarded-For $remote_addr;

    return 307 https://$host$request_uri;
    client_max_body_size 500M; # In case we have an extra large payload capture
}

server {
    # Redirect HTTPS to www
    listen 443;
    ssl on;
    ssl_certificate /etc/nginx/ssl/fakedomain.com.crt; # Wildcard SSL certificate
    ssl_certificate_key /etc/nginx/ssl/fakedomain.com.key; # Wildcard SSL certificate key

    server_name fakedomain.com;
    location / {
        rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
    }
}

server {
    # API proxy
    listen 443;
    ssl on;
    ssl_certificate /etc/nginx/ssl/fakedomain.com.crt; # Wildcard SSL certificate
    ssl_certificate_key /etc/nginx/ssl/fakedomain.com.key; # Wildcard SSL certificate key

    server_name *.fakedomain.com;
    access_log /var/log/nginx/fakedomain.com.vhost.access.log;
    error_log /var/log/nginx/fakedomain.com.vhost.error.log;

    client_max_body_size 500M;

    location / {
        proxy_pass  http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}

server {
    # Redirect api to HTTPS
    listen 80;
    server_name api.fakedomain.com; # Subdomain for API server
    proxy_set_header X-Forwarded-For $remote_addr;

    return 307 https://api.fakedomain.com$request_uri;
    client_max_body_size 500M; # In case we have an extra large payload capture
}

server {
   # Redirect www to HTTPS
   listen 80;
   server_name www.fakedomain.com;
   location / {
       rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
   }
}

server {
   # GUI proxy
   listen 443;
   server_name www.fakedomain.com;
   client_max_body_size 500M;
   ssl on;
   ssl_certificate /etc/nginx/ssl/fakedomain.com.crt; # Wildcard SSL certificate
   ssl_certificate_key /etc/nginx/ssl/fakedomain.com.key; # Wildcard SSL certificate key


   location / {
       proxy_pass  http://localhost:1234;
       proxy_set_header Host $host;
   }
}
"""


def print_header():
    print """
 __   __ _____ _____   _    _             _
 \ \ / // ____/ ____| | |  | |           | |
  \ V /| (___| (___   | |__| |_   _ _ __ | |_ ___ _ __
   > <  \___ \\\\___ \  |  __  | | | | '_ \| __/ _ \ '__|
  / . \ ____) |___) | | |  | | |_| | | | | ||  __/ |
 /_/ \_\_____/_____/  |_|  |_|\__,_|_| |_|\__\___|_|


                                           Setup Utility
"""


def build_docker_base():
    """ Automatically builds the Docker base images with dependancies """
    print INFO + "Building base Python image, please wait..."
    os.system(DOCKER + " build ./docker/python -t xsshunter_python")
    print INFO + "Building base Nginx image, please wait..."
    os.system(DOCKER + " build ./docker/nginx -t xsshunter_nginx")


def nginx_conf(settings):
    print "What is the base domain name you will be using? "
    print "(ex. localhost, www.example.com)"
    hostname = raw_input(PROMPT + "Domain? ")
    if hostname != "":
        settings["domain"] = hostname
    return NGINX_TEMPALTE.replace("fakedomain.com", settings["domain"])


def email_conf(settings):
    print "Great! Now let's setup your Mailgun account to send XSS alerts to."
    print "We'll need yo API key (ex. key-8da843ff65205a61374b09b81ed0fa35)"
    settings["mailgun_api_key"] = raw_input(PROMPT + "API key: ")
    print ""

    print "What is your Mailgun domain? (ex. example.com)"
    settings["mailgun_sending_domain"] = raw_input(PROMPT + "Mailgun domain: ")
    print ""

    print "What email address is sending the payload fire emails?: "
    print "(ex. no-reply@example.com)"
    settings["email_from"] = raw_input(PROMPT + "Sending email address: ")
    print ""

    print "[?] Where should abuse/contact emails go?: "
    print "(ex. yourpersonal@gmail.com)"
    settings["abuse_email"] = raw_input(PROMPT + "Abuse/Contact email: ")
    print ""


def database_conf(settings):
    print "[?] What postgres user is this service using? "
    print "(ex. xsshunter)"
    settings["postgreql_username"] = raw_input(PROMPT + "Postgres username: ")
    print ""

    print "What is the postgres user's password? (ex. @!$%@^%UOFGJOEJG$)"
    settings["postgreql_password"] = raw_input(PROMPT + "Postgres password: ")
    print ""

    print "What is the postgres user's DB? (ex. xsshunter)"
    settings["postgres_db"] = raw_input(PROMPT + "Postgres DB: ")
    print ""


def secrets_conf(settings):
    print INFO + " Generating cookie secret..."
    settings["cookie_secret"] = os.urandom(32).encode('hex')


def print_footer(hostname):
    print """
Setup complete! Please now copy the 'default' file to /etc/nginx/sites-enabled/default
This can be done by running the following:
sudo cp default /etc/nginx/sites-enabled/default

Also, please ensure your wildcard SSL certificate and key are available at the following locations:
/etc/nginx/ssl/""" + hostname + """.crt; # Wildcard SSL certificate
/etc/nginx/ssl/""" + hostname + """.key; # Wildcard SSL key

Good luck hunting for XSS!
							-xsshunter team
"""


def main():
    settings = {
        "email_from": "",
        "mailgun_api_key": "",
        "mailgun_sending_domain": "",
        "domain": "",
        "abuse_email": "",
        "cookie_secret": "",
    }
    print_header()

    # Docker base images
    msg = PROMPT + "Should I build the docker base images [y/n]? "
    if raw_input(msg).lower() == "y":
        build_docker_base()

    # Email setup
    msg = PROMPT + "Should I setup email support [y/n]? "
    if raw_input(msg).lower() == "y":
        email_conf(settings)

    # Database setup
    msg = PROMPT + "Should I setup the databse [y/n]? "
    if raw_input(msg).lower() == "y":
        database_conf(settings)

    yaml_config = yaml.dump(settings, default_flow_style=False)
    file_handler = open(DOCKERCOMPOSEFILE, "w")
    file_handler.write(yaml_config)
    file_handler.close()

    print "[*] Minting new nginx configuration file..."
    file_handler = open("default", "w")
    conf = nginx_conf(settings)
    file_handler.write(conf)
    file_handler.close()

    print_footer(settings["hostname"])
    msg = PROMPT + "Should I start the whole stack [y/n]? "
    if raw_input(msg).lower() == "y":
        os.system("docker-compose up -f %s" % DOCKERCOMPOSEFILE)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
