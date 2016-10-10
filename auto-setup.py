#!/usr/bin/env python
"""
A basic script to generate docker-compose configuration files,
this is the easiest way to get the whole stack running on one machine.
"""

import os
import urllib2
import platform

from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE


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
DOCKER_HELP_URL = "https://docs.docker.com/engine/installation/linux/ubuntulinux/#create-a-docker-group"
DOCKER_FOR_LINUX = 'https://get.docker.com/'
DOCKER_FOR_OSX = 'https://download.docker.com/mac/stable/Docker.dmg'
DOCKER_COMPOSE_FILENAME = "docker-compose.yml"


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


def yes_no_prompt(message):
    """ Yes/No prompt returns True for 'y' or 'yes' """
    return raw_input(PROMPT + message + "? [Y/n]: ").lower().strip() in [
        "y", "yes"
    ]


try:
    import yaml
except ImportError:
    if yes_no_prompt("PyYAML is not installed, should I install it"):
        child = Popen("sudo pip install PyYAML", shell=True)
        child.wait()
        if child.returncode == 0:
            print INFO + "Successfully installed PyYAML, re-run this script"
        else:
            print WARN + "PyYAML installation did not exit cleanly"
    else:
        print WARN + "Please install PyYAML; 'pip install PyYAML'"
    os._exit(1)


def build_docker_base():
    """ Automatically builds the Docker base images with dependancies """
    # Build Python base image
    print INFO + "Building base Python image, please wait..."
    py_base = Popen(DOCKER + " build ./docker/python -t xsshunter_python",
                    shell=True)
    py_base.wait()
    if py_base.returncode != 0:
        print WARN + "Python base image build did not exit cleanly"
        if yes_no_prompt("Would you like to try again?"):
            build_docker_base()
    # Build Nginx base image
    print INFO + "Building base Nginx image, please wait..."
    nginx_base = Popen(DOCKER + " build ./docker/nginx -t xsshunter_nginx",
                       shell=True)
    nginx_base.wait()
    if nginx_base.returncode != 0:
        print WARN + "Nginx base image build did not exit cleanly"
        if yes_no_prompt("Would you like to try again?"):
            build_docker_base()


def nginx_conf(compose, is_prod):
    print "What is the base domain name you will be using? "
    print "(ex. localhost, www.example.com)"
    hostname = raw_input(PROMPT + "Root domain? ").strip()
    if len(hostname):
        compose["services"]["api"]["environment"].append(
            "XSSHUNTER_DOMAIN=%s" % hostname
        )
        with open("./gui/nginx/xsshunter.template", "rb") as fp:
            conf = fp.read()
        print INFO + "Saving new config to: ./gui/nginx/xsshunter"
        with open("./gui/nginx/xsshunter", "wb") as fp:
            fp.write(conf.replace("fakedomin.com", hostname))
    else:
        print WARN + "Invalid hostname (length 0), skipping Nginx setup"


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
        compose["services"]["sql"]["ports"] = ['5432:5432']


def secrets_conf(compose, is_prod):
    print INFO + " Generating fresh cookie secret..."
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
                'expose': ['8888'],
                'volumes': [
                    "./api/uploads:/opt/xsshunter/uploads"
                ],
                'depends_on': ['sql']
            },
            'web': {
                'build': './gui',
                'volumes': [
                    "./gui/ssl:/etc/ngix/ssl"
                ],
                'ports': ['80', '443'],
                'depends_on': ['api']
            }
        },
    }

    # Docker base images
    is_prod = yes_no_prompt("Is this a production setup (`no` for dev setup)")
    if is_prod:
        print INFO + "%sProduction build%s (no debug features)" % (
            BOLD, W
        )
    else:
        print WARN + "%sDevelopement build%s, debug features are enabled!" % (
            BOLD, W
        )
        compose["services"]["api"]["environment"].append("XSSHUNTER_DEBUG=1")

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
    print "-" * 60
    if yes_no_prompt("Should I save all of the current settings"):
        with open(DOCKER_COMPOSE_FILENAME, "w") as fp:
            fp.write(yaml_config)

    if yes_no_prompt("Should I build the main docker images for you now"):
        docker_compose = Popen("docker-compose build", shell=True)
        docker_compose.wait()
        if docker_compose.returncode != 0:
            print WARN + "Docker compose build failed, not sure why ..."
        else:
            print INFO + "Built all docker images successfully!"

    print_footer()
    if yes_no_prompt("Should I fire up the whole stack for you now"):
        try:
            os.system("docker-compose up")
        except KeyboardInterrupt:
            pass
    print "\n\n"
    print INFO + "In the future you can start everything with:\n"
    print "\t'docker-compose up' or 'docker-compose up -d' for detached mode\n"


def docker_version():
    """ Checks the docker version, returns None if docker isn't installed """
    try:
        return Popen([DOCKER, '--version'], stdout=PIPE).stdout.read().strip()
    except OSError:
        return None


def linux_docker_install():
    """ Downloads Docker's own setup script and executes it """
    response = urllib2.urlopen(DOCKER_FOR_LINUX)
    script = NamedTemporaryFile(delete=False)
    script.write(response.read())
    script.close()
    os.chmod(script.name, "644")
    child = Popen("sudo sh %s" % script.name, shell=True)
    child.wait()
    if child.returncode != 0:
        print WARN + "Docker installation did not exit cleanly"
    os.unlink(script.name)


def osx_docker_install():
    """ Download the Docker for OSX .dmg and opens it """
    print INFO + "Downloading Docker for OSX, please wait ..."
    response = urllib2.urlopen(DOCKER_FOR_OSX)
    dmg = NamedTemporaryFile(delete=False)
    dmg.write(response.read())
    dmg.close()
    installer_path = os.path.join(os.getcwd(), "docker-for-osx.dmg")
    os.rename(dmg.name, installer_path)
    print INFO + "Docker for OSX downloaded to: %s" % installer_path
    child = Popen("open -W %s" % installer_path, shell=True)
    child.wait()
    if child.returncode != 0:
        print WARN + "Docker install did not exist cleanly"
    os.unlink(installer_path)


def docker_setup():
    print WARN + "Docker is not installed or is not on the system path"
    if yes_no_prompt("Would you like me to install docker"):
        if platform.system().lower() in ['linux']:
            linux_docker_install()
        elif platform.system().lower() in ['darwin']:
            osx_docker_install()
    else:
        print WARN + """Skipping Docker installation, but this is probably
    going to break a lot of stuff, don't say I didn't warn you."""


def user_has_docker_permissions():
    """ Checks to see if the current user has permission to talk to docker """
    try:
        child = Popen([DOCKER, "ps"], stdout=PIPE, stderr=PIPE)
        child.wait()
        return True if child.returncode == 0 else False
    except OSError:
        return False


if __name__ == "__main__":
    #
    # We just check for the dependancies here and then execute main()
    #
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if platform.system().lower() not in ['linux', 'darwin']:
        print "[!] Fatal error; unsupported platform switch to Linux or OSX"
        os._exit(3)
    try:
        print_header()
        if docker_version() is None:
            docker_setup()
        if docker_version() is not None:
            print INFO + "PyYAML is installed (PyYAML v%s)" % yaml.__version__
            print INFO + "Docker is installed (%s)" % docker_version()
            if user_has_docker_permissions():
                print INFO + "The current user can execute docker commands!"
            else:
                print WARN + """The current user cannot execute docker commands

    You'll probably have to add the current user to a group that has permission
    to execute docker commands or execute this script as root.

    For more help see: %s
""" % DOCKER_HELP_URL
                os._exit(4)
            main()
    except KeyboardInterrupt:
        print "\n\n" + WARN + "User exit"
