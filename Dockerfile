FROM alpine:latest

# Install python, pip and libs 
RUN apk add --update python \
                    ca-certificates \
                    py-pip \
                    python-dev \
                    bash \
                    libffi-dev \
                    libressl-dev \
                    cyrus-sasl-dev \
                    musl-dev \
                    gcc \ 
                    g++ \ 
                    mariadb-dev \
                    postgresql-dev

ADD requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Add our code
ADD . /opt/bit/
WORKDIR /opt/bit

# Expose is NOT supported by Heroku
# EXPOSE 5000       

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku            
# CMD gunicorn --bind 0.0.0.0:$PORT wsgi 

CMD python bit runserver
