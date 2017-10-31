FROM chiter/codesmart-bit:pip

# Copy new files to work dir
ADD . /var/www/bit
WORKDIR /var/www/bit
