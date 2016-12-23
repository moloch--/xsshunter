####################################
#
#  Dockerfile for Nginx+PageSpeed/Spdy
#  v0.0.2 - By Moloch
FROM debian:latest
MAINTAINER moloch

ENV DEBIAN_FRONTEND noninteractive
ENV PAGESPEED_VER 1.11.33.3
ENV NGINX_VER 1.11.4


#
# > Fix Apt's broke ass
# https://github.com/docker-library/buildpack-deps/issues/40
#
RUN echo \
   'deb ftp://ftp.us.debian.org/debian/ jessie main\n \
    deb ftp://ftp.us.debian.org/debian/ jessie-updates main\n \
    deb http://security.debian.org jessie/updates main\n' \
    > /etc/apt/sources.list



#
# > Install/Compile Nginx + PageSpeed/Spdy
#
RUN apt-get update --fix-missing \
	&& apt-get install --fix-missing -y build-essential zlib1g-dev libpcre3 libpcre3-dev openssl libssl-dev libperl-dev wget ca-certificates logrotate libgeoip-dev git

RUN (wget -O - https://github.com/pagespeed/ngx_pagespeed/archive/v${PAGESPEED_VER}-beta.tar.gz | tar zxf - -C /tmp) \
	&& (wget -O - https://dl.google.com/dl/page-speed/psol/${PAGESPEED_VER}.tar.gz | tar zxf - -C /tmp/ngx_pagespeed-${PAGESPEED_VER}-beta/) \
	&& (wget -O - https://nginx.org/download/nginx-${NGINX_VER}.tar.gz | tar zxf - -C /tmp) \
	&& cd /tmp/nginx-${NGINX_VER} \
	&& ./configure --prefix=/etc/nginx/ --sbin-path=/usr/sbin/nginx --add-module=/tmp/ngx_pagespeed-${PAGESPEED_VER}-beta \
		--with-cc-opt='-O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2' \
		--with-http_ssl_module \
		--with-http_realip_module \
		--with-http_addition_module \
		--with-http_sub_module \
		--with-http_gunzip_module \
		--with-http_gzip_static_module \
		--with-http_random_index_module \
		--with-http_secure_link_module \
		--with-http_stub_status_module \
		--with-http_v2_module \
		--with-http_geoip_module \
		--with-mail \
		--with-mail_ssl_module \
		--with-file-aio \
		--with-ipv6 \
	&& make install


#
# > Install NodeJS v4 and NPM v3
#
WORKDIR /tmp
RUN wget https://deb.nodesource.com/setup_4.x
RUN chmod +x ./setup_4.x \
	&& ./setup_4.x \
	&& rm -f ./setup_4.x
RUN apt-get install -y nodejs
RUN npm install -g npm@latest
RUN npm install -g angular-cli@1.0.0-beta.22-1 && npm install -g is-my-json-valid


#
# > Clean Up
#
RUN rm -Rf /tmp/* \
	&& apt-get purge -yqq wget build-essential \
	&& apt-get autoremove -yqq \
	&& apt-get clean


#
# > Make Nginx Directories
#
RUN mkdir /var/ngx_pagespeed_cache && chmod 777 /var/ngx_pagespeed_cache
RUN mkdir /etc/nginx/sites-enabled \
	&& mkdir /etc/nginx/sites-available \
	&& mkdir /etc/nginx/ssl \
	&& mkdir /var/log/nginx


#
# > Redirect Logs to STDOUT/STDERR
#
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log


#
# > Expose Ports
#
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
