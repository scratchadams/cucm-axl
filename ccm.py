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
 
disable_warnings(InsecureRequestWarning)
 
username = ''
password = ''
host = ''
 
wsdl = 'schema/current/AXLAPI.wsdl'
location = 'https://{host}:8443/axl/'.format(host=host)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"
 
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)
 
transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)
 
def show_history():
    for item in [history.last_sent, history.last_received]:
        print etree.tostring(item["envelope"], encoding="unicode", pretty_print=True)

def trans_pattern_lookup(ext):

    try:
        resp = service.listTransPattern(searchCriteria={'pattern':'%'},
                returnedTags={'pattern': '', 'calledPartyTransformationMask': '', 'description': ''})
    except Fault:
        show_history()

    
    for x in resp['return']['transPattern']:
        if (x['calledPartyTransformationMask'] == ext):
            print "Pattern: " + x['pattern'] + " description: " + x['description']
    
    #print resp['return']['transPattern'][0]['calledPartyTransformationMask']

def main():
    if len(sys.argv) < 2:
        print "Usage: python ccm.py [extension]"
        exit()

    trans_pattern_lookup(sys.argv[1])

main()

