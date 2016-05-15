import nmap
import sqlite3
import inspect

conn = sqlite3.connect('connection-log.db')
table_name = 'connection_log'

# Check whether our connection table exists. If it does not: create it.
cur = conn.cursor()
cur.execute('create table if not exists %s (mac text, timestamp datetime, is_available boolean)' % table_name)

# Select latest states of all known MACs.
cur.execute('select log.mac, log.is_available from %s as log\
             join (select mac, max(timestamp) as timestamp from %s group by mac) x\
             on log.mac = x.mac and log.timestamp = x.timestamp' % (table_name, table_name))
status_list = [x for x in cur]

print status_list

nm = nmap.PortScanner()

nm.scan(hosts='192.168.2.0/24', arguments='-n -sP -PE -PA21,23,80,3389')
hosts_list = [(x, nm[x]['status']['state'], nm[x]['vendor']) for x in nm.all_hosts()]

print hosts_list

for host, status, vendor in hosts_list:
    print('{0}:{1}:{2}'.format(host, status, vendor))

    if len(vendor) > 0:
        mac = vendor.keys()[0]
        cur.execute('insert into %s (mac, timestamp, is_available) values (?, datetime(\'now\'), ?)' % table_name, (mac, 1))
        conn.commit()

        # for key, value in vendor.items():
        #     print(key, value)

    # Check the previous value of 


conn.close()
