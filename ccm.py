from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from lxml import etree
import sys
import getopt
 
disable_warnings(InsecureRequestWarning)
 
username = ''
password = ''
host = ''
 
wsdl = 'schema/current/AXLAPI.wsdl'
location = 'https://{host}:8443/axl/'.format(host=host)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

wsdl_realtime = 'https://' + host + ':8443/realtimeservice/services/RisPort?wsdl'
location_realtime = 'https://' + host + ':8443/realtimeservice/services/RisPort'

session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)
 
transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)

client_realtime = Client(wsdl=wsdl_realtime, transport=transport, plugins=[history])
#service_realtime = client_realtime.create_service(binding, location)


def show_history():
    for item in [history.last_sent, history.last_received]:
        print etree.tostring(item["envelope"], encoding="unicode", pretty_print=True)

def ip_lookup(ip_add):
    try:
        resp = client_realtime.service.SelectCmDevice('', {'SelectBy':'Name', 'Status':'Registered', 'Class':'Phone'})

        cm_nodes = resp['body']['SelectCmDeviceResult']['CmNodes']
        devices = resp['body']['SelectCmDeviceResult']['CmNodes'][1]['CmDevices']
        
        for node in cm_nodes:
            devices = node['CmDevices']
            
            for dev in devices:
                if dev['IpAddress'] == ip_add:
                    return dev

        return None

    except Fault:
        show_history()

def trans_pattern_lookup(ext):
    try:
        resp = service.listTransPattern(searchCriteria={'pattern':'%'},
                returnedTags={'pattern': '', 'calledPartyTransformationMask': '', 'description': ''})
    except Fault:
        show_history()

    #resp = service.listTransPattern('%')
    for x in resp['return']['transPattern']:
        #print x['calledPartyTransformationMask']

        if (x['calledPartyTransformationMask'] == ext):
            print "Pattern: " + x['pattern'] + " description: " + x['description']
    
    #print resp['return']['transPattern'][0]['calledPartyTransformationMask']

def main():
    cmd_opts = ["ip=", "css=", "login=", "trans"]
    short_opts = "i:c:l:t:"
    
    if len(sys.argv) < 3:
        print "Usage: python ccm.py [options] [value]"
        print "--ip [IP Address] (search by IP)"
        print "--css [Search Space] (list all devices in CSS)"
        print "--login [User Name] (list all devices associated with user)"
        print "--trans [Extension] (list all translation patterns associated with extension)"

        sys.exit(1)


    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_opts, cmd_opts)
    except getopt.error as err:
        print "error: " + str(err)
        sys.exit(2)

    print "arguments: " + str(arguments)
    
    for arg, val in arguments:
        print "arg: " + arg
        if arg in ("-i", "--ip"):
            print "Search by IP: " + val
            print ip_lookup(val)

    
    #trans_pattern_lookup(sys.argv[1])

main()
#ip_lookup('10.15.10.67')
