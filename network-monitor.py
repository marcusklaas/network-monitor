#!/usr/bin/python

import nmap
import sqlite3
import params

conn = sqlite3.connect(params.database_path)

# Check whether our connection table exists. If it does not: create it.
cur = conn.cursor()
cur.execute('create table if not exists %s (mac text, timestamp datetime, is_available boolean)' % params.table_name)

# Create index to speed up aggregation
cur.execute('create index if not exists mac_time on %s (mac, timestamp)' % params.table_name)

while True:
    nm = nmap.PortScanner()
    nm.scan(hosts=params.subnetwork, arguments='-n -sP -PE -PA21,23,80,3389')
    hosts_list = [(nm[x]['vendor'].keys()[0], 1) for x in nm.all_hosts() if len(nm[x]['vendor']) > 0]

    # Select latest states of all known MACs.
    cur.execute('select log.mac, log.is_available from %s as log\
                 join (select mac, max(timestamp) as timestamp from %s group by mac) x\
                 on log.mac = x.mac and log.timestamp = x.timestamp' % (params.table_name, params.table_name))
    status_list = list(cur)
    update_query = 'insert into %s (mac, timestamp, is_available) values (?, datetime(\'now\'), ?)' % params.table_name

    for mac, status in set(hosts_list) - set(status_list):
        cur.execute(update_query, (mac, 1))

    for mac, status in set([x for x in status_list if x[1] == 1]) - set(hosts_list):
        cur.execute(update_query, (mac, 0))

    conn.commit()
    print "Finished loop"

conn.close()
