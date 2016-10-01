
#
#  Dockerfile for Frontend Web
#  v0.2.0 - By Moloch
FROM xsshunter_nginx:latest
MAINTAINER moloch

ENV APP_NAME xsshunter-client

RUN mkdir -p /var/www/${APP_NAME}
ADD . /var/www

#
# > Nginx Configs
#
WORKDIR /var/www
RUN mv ./nginx/xsshunter /etc/nginx/sites-available/xsshunter
RUN mv ./nginx/nginx.conf /etc/nginx/conf/nginx.conf && rm -rf ./nginx
RUN ln -s /etc/nginx/sites-available/xsshunter /etc/nginx/sites-enabled/xsshunter

#
# > Build client code
#
WORKDIR /var/www/${APP_NAME}
RUN npm install --unsafe-perm
RUN ng build

#
# > Expose volumes
#
VOLUME ["/etc/nginx/ssl", "/var/www/", "/var/ngx_pagespeed_cache"]


#
# > Expose ports
#
EXPOSE 80
EXPOSE 443
