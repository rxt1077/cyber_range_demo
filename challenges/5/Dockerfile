FROM httpd:2.4
COPY httpd.conf /usr/local/apache2/conf/
RUN rm /usr/local/apache2/htdocs/*
COPY ./public-html/ /usr/local/apache2/htdocs/
