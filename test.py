import nmap

nm = nmap.PortScanner()

nm.scan(hosts='192.168.2.0/24', arguments='-n -sP -PE -PA21,23,80,3389')
hosts_list = [(x, nm[x]['status']['state'], nm[x]['vendor']) for x in nm.all_hosts()]
for host, status, vendor in hosts_list:
    print('{0}:{1}:{2}'.format(host, status, vendor))
