FROM chiter/codesmart-bit:pip

# Copy new files to work dir
WORKDIR /var/www/bit
ADD . /var/www/bit


RUN unlink /var/www/bit/incubator-superset/superset/static/assets
RUN cd /var/www/bit/incubator-superset/superset/static/ && ln -s /var/www/bit/incubator-superset/superset/assets/ assets

# CMD ["python", "bitstart.py", "runserver"]