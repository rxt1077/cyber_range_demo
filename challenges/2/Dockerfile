FROM httpd
RUN sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" conf/httpd.conf 
RUN mkdir -p htdocs/red/
COPY herring.gif htdocs/red/
RUN mkdir -p htdocs/secrets/
COPY flag.html htdocs/secrets/
