#!/usr/bin/python

# requerimientos: python3, scapy, numpy
import sys, os, argparse
import numpy as np

# from math import log as LOG
from scapy.all import *
from time import *

# Manejo de argumentos
parser = argparse.ArgumentParser(description='Implementacion en scapy de traceroute')
parser.add_argument('--destination-host', '-d', dest='host', default='google.com', help='host al cual se quiere hacer el traceroute (default: google.com)')
parser.add_argument('--ttl', '-t', dest='ttl',  type=int, default=30, help='ttl de los paquetes (default: 30)')
parser.add_argument('--queries', '-q', dest='queries',  type=int, default=1, help='numero de paquetes que se le envia a cada hop (default: 1)')
parser.add_argument('--timeout', '-o', dest='timeout', default=1, help='timeout del envio de cada paquete (default: 1s)')
parser.add_argument('--verbose', '-v', action='store_true', help='agregar si se desea verbosidad de la herramienta (default: no)')
args = parser.parse_args()

# Diccionario que para cada ttl, guarda una lista con tuplas (host, rtt)
responses = {}

ttl_range = range(1, args.ttl+1)

def print_route(rs):
    table = {}
    last_rtt = 0
    for ttl in ttl_range:
        if ttl not in rs: continue

        # r = (src, rtt)
        ips = ",".join(list(set([ r[0] for r in rs[ttl] ])))
        avg_rtt = average( [ r[1] for r in rs[ttl] ] )
        std_rtt = std( [ r[1] for r in rs[ttl] ] )

        if avg_rtt-last_rtt<0.0:
            table[ttl] = (avg_rtt, std_rtt, 0, ips)
        else:
            table[ttl] = (avg_rtt, std_rtt, avg_rtt-last_rtt, ips)
            last_rtt = avg_rtt
    
    print("ttl\tavg_rtt\tstd_rtt\td_rtt\tips")
    for ttl in ttl_range:
        if ttl not in table:
            print(ttl, "\t*\t*\t*\t*")
        else:
            # table[ttl] = (avg_rtt, std_rtt, delta_rtt, ips)
            print("%d\t" % (ttl) + "%.2f\t%.2f\t%.2f\t%s" % table[ttl])


# Recordar que se pueden invertir los siguientes ciclos.
for ttl in ttl_range:
    for i in range(args.queries):
        probe = IP(dst=args.host, ttl=ttl) / ICMP()

        t_i = time()
        # Envia un paquete, y devuelve la respuesta (si la hubo)
        ans = sr1(probe, verbose=False, timeout=args.timeout)
        t_f = time()

        if ans is not None:
            rtt = (t_f - t_i)*1000
            # Otra manera: el paquete enviado tiene su timestamp en sent_time, y el recibido en time. 
            #rtt = (ans.time - probe.sent_time)*1000

            if ttl not in responses: responses[ttl] = []
            responses[ttl].append((ans.src, rtt))

        os.system('clear')
        print("%s, iteracion %d" %(args.host, i+1))
        print_route( responses )

        # Tipo 0: echo-reply
        if ans is not None and ans.type==0: break

# Promedio
avgs = []
mins = []
for ttl in ttl_range:
    if ttl not in responses: continue
    rtts = [ r[1] for r in responses[ttl] ]
    avgs.append(np.average(rtts))
    mins.append(min(rtts))
    print("%d, %d" %(avgs[-1], mins[-1]))


# 2 - Outliers

from scipy import stats
import math

# The Modified Thompson tau 
def tau(n):
    # The critical students t value alpha = 0.05; df = n-2, https://stackoverflow.com/questions/19339305/python-function-to-get-the-t-statistic
    tinv = stats.t.ppf(1-0.025, n-2)  
    return tinv * (n - 1) / (math.sqrt(n) * math.sqrt(n - 2 + tinv ** 2))

#La onda es que vengan ordenados de menor a mayor, entonces si aparece un outlier, como dice en el paper volvemos a iterar pero sacando este ultimo
#Asi que el metodo devuelve la cantidad de no outliers 
def outliers_detection(hop_samples):
    n = len(hop_samples)
    mean = np.mean(hop_samples)
    std = np.std(hop_samples)
    t = tau(n)
    tS = t * std

    last_sample = hop_samples[-1]
    delta = np.absolute(last_sample - mean)

    if delta < tS:
        return n

    else:
        hop_samples.pop()
        return outliers_detection(hop_samples)

print(outliers_detection(sorted(avgs)))