#!/usr/bin/python

import sys
import sqlite3
import qhue
import params

conn = sqlite3.connect(params.database_path)
cur = conn.cursor()
bridge = qhue.Bridge(params.hue_bridge_ip, params.hue_username)

# Check whether our connection table exists. If it does not: print error
# message and abort.
cur.execute('SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=?', (params.table_name,))
if cur.next()[0] != 1:
    print 'Cannot find connection log database. Exiting.'
    sys.exit(1)

cur.execute('select 0 from %s\
             where mac = ?\
             and timestamp >= datetime(\'now\', \'-%s minutes\')\
             and is_available = 1' % (params.table_name, params.phone_timeout_minutes),
            (params.phone_mac,))

if sum(1 for _ in cur) == 0:
    # Phone hasn't been detected for a while: turn off da lights!
    print "Turn off the lights"
    for index in bridge.lights():
        bridge.lights[index].state(on=False)
else:
    print "Phone detected in last %s minutes; boss is probably still home" % params.phone_timeout_minutes
