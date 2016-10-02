#!/usr/bin/env python

import yaml
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
WARN = "%s%s[!]%s " % (BOLD, R, W)

DOCKER = "docker"
DOCKERCOMPOSEFILE = "docker-compose.yml"


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


def yes_no_prompt(msg):
    return raw_input(PROMPT + msg + " [Y/n]? ").lower().strip() in ["y", "yes"]


def build_docker_base():
    """ Automatically builds the Docker base images with dependancies """
    print INFO + "Building base Python image, please wait..."
    os.system(DOCKER + " build ./docker/python -t xsshunter_python")
    print INFO + "Building base Nginx image, please wait..."
    os.system(DOCKER + " build ./docker/nginx -t xsshunter_nginx")


def nginx_conf(compose, is_prod):
    print "What is the base domain name you will be using? "
    print "(ex. localhost, www.example.com)"
    hostname = raw_input(PROMPT + "Root domain? ")
    if hostname != "":
        compose["services"]["api"]["environment"].append(
            "XSSHUNTER_DOMAIN=%s" % hostname
        )


def email_conf(compose, is_prod):
    print "Great! Now let's setup your Mailgun account to send XSS alerts to."
    print "We'll need yo API key (ex. key-8da843ff65205a61374b09b81ed0fa35)"
    mailgun_api_key = raw_input(PROMPT + "API key: ")
    print ""
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_MAILGUN_API_KEY=%s" % mailgun_api_key
    )

    print "What is your Mailgun domain? (ex. example.com)"
    mailgun_sending_domain = raw_input(PROMPT + "Mailgun domain: ")
    print ""
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_MAILGUN_SENDING_DOMAIN=%s" % mailgun_sending_domain
    )

    print "What email address is sending the payload fire emails?: "
    print "(ex. no-reply@example.com)"
    email_from = raw_input(PROMPT + "Sending email address: ")
    print ""
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_EMAIL_FROM=%s" % email_from
    )

    print "Where should abuse/contact emails go? "
    print "(ex. yourpersonal@gmail.com)"
    email_abuse = raw_input(PROMPT + "Abuse/Contact email: ")
    print ""
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_EMAIL_ABUSE=%s" % email_abuse
    )


def database_conf(compose, is_prod):
    """ Sets up the Postgres database """
    print "What Postgres username? (ex. xsshunter)"
    db_username = raw_input(PROMPT + "Postgres username: ")
    print ""
    compose["services"]["sql"]["environment"].append(
        "POSTGRES_USER=%s" % db_username
    )
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_SQL_USER=%s" % db_username
    )

    print "What is the Postgres user's password? (ex. @!$%@^%UOFGJOEJG$)"
    db_password = raw_input(PROMPT + "Postgres password: ")
    print ""
    compose["services"]["sql"]["environment"].append(
        "POSTGRES_PASSWORD=%s" % db_password
    )
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_SQL_PASSWORD=%s" % db_password
    )

    print "What is the name of the Postgres database? (ex. xsshunter)"
    db_name = raw_input(PROMPT + "Postgres DB: ")
    print ""
    compose["services"]["sql"]["environment"].append(
        "POSTGRES_DB=%s" % db_name
    )
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_SQL_DATABASE=%s" % db_name
    )

    if not is_prod:
        print WARN + "Exposing database port 5432 for debugging"
        compose["services"]["sql"]["ports"] = ['"5432:5432"']
    return db_username, db_password, db_name


def secrets_conf(compose, is_prod):
    print INFO + " Generating cookie secret..."
    secret = os.urandom(32).encode('hex')
    compose["services"]["api"]["environment"].append(
        "XSSHUNTER_COOKIE_SECRET=%s" % secret
    )


def print_footer():
    print """
    Also, please ensure your wildcard SSL certificate and key are available at
    the following locations:

    ./gui/ssl/my.crt # Wildcard SSL certificate
    ./gui/ssl/my.key # Wildcard SSL key

        Good hunting,
           -xsshunter team
"""


def main():
    """ Walks the user thru the entire setup of XSS Hunter """
    compose = {
        'version': '2',
        'services': {
            'sql': {
                'image': 'postgres:latest',
                'environment': []
            },
            'api': {
                'build': './api',
                'environment': [
                    "XSSHUNTER_LISTEN_PORT=8888",
                ],
                'expose': ["8888"],
                'volumes': [],
                'depends_on': ['sql']
            },
            'web': {
                'build': './gui',
                'environment': [],
                'volumes': [],
                'ports': ["80", "443"],
                'depends_on': ['api']
            }
        },
    }
    print_header()

    # Docker base images
    is_prod = yes_no_prompt("Is this a production setup (`no` for dev setup)")
    if is_prod:
        print INFO + "%sProduction deployment%s (no debug features)" % (
            BOLD, W
        )
    else:
        print WARN + "%sDevelopement deployment%s, debug features enabled!" % (
            BOLD, W
        )
        compose["services"]["api"]["environment"].append("XSSHUNTER_DEBUG=1")
    print ""

    # Docker base images
    if yes_no_prompt("Should I build the docker base images for you"):
        build_docker_base()

    # Database setup
    if yes_no_prompt("Should I setup the database now"):
        database_conf(compose, is_prod)

    # Email setup
    if yes_no_prompt("Should I setup email support"):
        email_conf(compose, is_prod)

    if yes_no_prompt("Should I configure Nginx for you"):
        print INFO + "Minting new nginx configuration file ..."
        nginx_conf(compose, is_prod)

    yaml_config = yaml.dump(compose, default_flow_style=False)
    print "-" * 60
    for index, line in enumerate(yaml_config.split('\n')):
        print "%02d. %s" % (index + 1, line)
    print "\n", "-" * 60
    if yes_no_prompt("Should I save all of the current settings"):
        with open(DOCKERCOMPOSEFILE, "w") as fp:
            fp.write(yaml_config)

    print_footer()
    if yes_no_prompt("Should I fire up the whole stack for you now"):
        os.system("docker-compose up -f %s" % DOCKERCOMPOSEFILE)
    else:
        print ""
        print INFO + "Okay no worries, you can start it yourself with:\n"
        print "docker-compose up\n"


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        main()
    except KeyboardInterrupt:
        print "\n\n" + WARN + "User exit"
