#!/usr/bin/env python3
from sys import exit
from jinja2 import Environment, FileSystemLoader
import os, webbrowser, data, argparse, geoip2.database

DB_FILE = "GeoLite2-City.mmdb"

def map_generator(replies):
	reader = geoip2.database.Reader(DB_FILE)

	hops = [ replies[x][0][0] for x in replies ]
	ubicaciones = []
	for hop in hops:
		try:
			print("Geolocalizing {}".format(hop))
			ubicaciones.append(reader.city(hop))
		except geoip2.errors.AddressNotFoundError:
			print("IP {} couldn't be geolocalized".format(hop))
			pass
		except Exception:
			pass

	# http://jinja.pocoo.org/docs/dev/api/
	jinjaenv = Environment(loader = FileSystemLoader('./templates'))
	template = jinjaenv.get_template('mapa.html')
	return template.render(ips=hops, labels=hops, ubicaciones=ubicaciones)



def main():
	parser = argparse.ArgumentParser(description='Dibujado de rutas en Google Maps')
	parser.add_argument('data', help='datos que se usan para dibujar el mapa')
	args = parser.parse_args()

	if not os.path.isfile(DB_FILE):
		print("Falta el archivo de base de datos; por favor corra make")
		exit(1)

	if not args.data in dir(data):
		print("No se conoce el set de datos '{}'".format(args.data))
		exit(1)

	outfile = 'mapita.html'
	with open(outfile, 'w') as map_file:
		map_file.write(map_generator(getattr(data, args.data)))
		webbrowser.open('file://' + os.path.realpath(outfile))



if __name__ == "__main__":
    main()