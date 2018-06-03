.PHONY: all clean

GEOLITE_DB = GeoLite2-City.mmdb
GEOLITE_DB_GZ = $(addsuffix .gz, $(GEOLITE_DB))

all: reqs

clean:
	rm -rf $(GEOLITE_DB)

$(GEOLITE_DB_GZ):
	wget "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"

$(GEOLITE_DB):
	if [ ! -f $(GEOLITE_DB) ]; then $(MAKE) $(GEOLITE_DB_GZ); gunzip GeoLite2-City.mmdb.gz; fi

reqs: $(GEOLITE_DB)
	pip3 install --user -r requirements.txt
