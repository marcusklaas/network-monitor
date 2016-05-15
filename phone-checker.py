#!/usr/bin/python

import sqlite3
import qhue
import params

conn = sqlite3.connect(params.database_path)
cur = conn.cursor()
bridge = qhue.Bridge(params.hue_bridge_ip, params.hue_username)

# TODO: check whether our connection table exists. If it does not: print error
# message and abort.

cur.execute('select 0 from connection_log\
             where mac = ?\
             and timestamp >= datetime(\'now\', \'-%s minutes\')\
             and is_available = 1' % params.phone_timeout_minutes, (params.phone_mac,))

if sum(1 for _ in cur) == 0:
    # Phone hasn't been detected for a while: turn off da lights!
    print "Turn off the lights"
    for index in bridge.lights():
        bridge.lights[index].state(on=False)
else:
    print "Phone detected in last %s minutes; boss is probably still home" % params.phone_timeout_minutes
