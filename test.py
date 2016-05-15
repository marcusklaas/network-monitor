import nmap
import sqlite3
import inspect

conn = sqlite3.connect('connection-log.db')
table_name = 'connection_log'

# Check whether our connection table exists. If it does not: create it.
cur = conn.cursor()
cur.execute('create table if not exists %s (mac text, timestamp datetime, is_available boolean)' % table_name)

while True:
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.2.0/24', arguments='-n -sP -PE -PA21,23,80,3389')
    hosts_list = [(nm[x]['vendor'].keys()[0], 1) for x in nm.all_hosts() if len(nm[x]['vendor']) > 0]

    # Select latest states of all known MACs.
    cur.execute('select log.mac, log.is_available from %s as log\
                 join (select mac, max(timestamp) as timestamp from %s group by mac) x\
                 on log.mac = x.mac and log.timestamp = x.timestamp' % (table_name, table_name))
    status_list = list(cur)

    for mac, status in set(hosts_list) - set(status_list):
        cur.execute('insert into %s (mac, timestamp, is_available) values (?, datetime(\'now\'), ?)' % table_name, (mac, 1))

    for mac, status in set([x for x in status_list if x[1] == 1]) - set(hosts_list):
        cur.execute('insert into %s (mac, timestamp, is_available) values (?, datetime(\'now\'), ?)' % table_name, (mac, 0))

    conn.commit()
    print "Finished loop"

conn.close()
