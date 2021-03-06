#
#  Dockerfile for XSS Hunter client
#
FROM xsshunter_nginx:latest
MAINTAINER moloch
MAINTAINER mandatory
ENV APP_NAME xsshunter-client


#
#  > Make directories, add code
#
RUN mkdir -p /var/www/${APP_NAME}
ADD . /var/www


#
# > Nginx Configs
#
WORKDIR /var/www

RUN mv ./nginx/probe /etc/nginx/sites-available/probe \
  && mv ./nginx/xsshunter /etc/nginx/sites-available/xsshunter
RUN mv ./nginx/nginx.conf /etc/nginx/conf/nginx.conf && rm -rf ./nginx
RUN ln -s /etc/nginx/sites-available/xsshunter /etc/nginx/sites-enabled/xsshunter \
  && ln -s /etc/nginx/sites-available/probe /etc/nginx/sites-enabled/probe


#
# > NPM Workaround
#
# Fix bug https://github.com/npm/npm/issues/9863
RUN cd $(npm root -g)/npm \
  && npm install fs-extra \
  && sed -i -e s/graceful-fs/fs-extra/ -e s/fs\.rename/fs.move/ ./lib/utils/rename.js


#
# > Build client code
#
WORKDIR /var/www/${APP_NAME}
RUN npm install --unsafe-perm
RUN ng build


#
# > Expose ports
#
EXPOSE 80
EXPOSE 443
