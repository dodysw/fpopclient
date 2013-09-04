import urllib, urllib2, json, base64, datetime
from pprint import pprint

class FreedomPop:
    refreshToken = None
    token = None
    tokenExpireTimestamp = None
    accessToken = None

    _apiUsername = "3726328870"
    _apiPassword = "pNp6TIgVm4viVadoyoUdxbsrfmiBwudN"
    endPoint = "https://api.freedompop.com"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _updateToken(self, url):
        req = urllib2.Request(url, data = "")
        req.add_header("Authorization", "Basic %s" % base64.encodestring("%s:%s" % (self._apiUsername, self._apiPassword)).replace("\n", ""))
        try:
            resp = urllib2.urlopen(req)
            data = json.loads(resp.read())
            self.accessToken = data["access_token"]
            self.refreshToken = data["refresh_token"]
            self.tokenExpireTimestamp = datetime.datetime.now() + datetime.timedelta(seconds = data["expires_in"])
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code
            print e.read()
            return False

        return True

    def _getAccessToken(self):
        params = urllib.urlencode(dict(username = self.username, password = self.password, grant_type = "password"))
        url = "%s/auth/token?%s" % (self.endPoint, params)
        return self._updateToken(url)

    def _refreshAccessToken(self):
        params = urllib.urlencode(dict(refresh_token = self.refreshToken, grant_type = "refresh_token"))
        url = "%s/auth/token?%s" % (self.endPoint, params)
        return self._updateToken(url)

    def initToken(self):
        if self.refreshToken is None:
            return self._getAccessToken()
        elif self.tokenExpireTimestamp < datetime.datetime.now():
            return self._refreshAccessToken()
        return True

    def _getBasic(self, command):
        if not self.initToken():
            return {}
        params = urllib.urlencode(dict(accessToken = self.accessToken))
        url = "%s/%s?%s" % (self.endPoint, command, params)
        try:
            buffer = urllib2.urlopen(url).read()
            return json.loads(buffer)
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code
            print e.read()
            return False

    def getUsage(self):
        return self._getBasic("user/usage")

    def getInfo(self):
        return self._getBasic("user/info")

    def getPlan(self, planId = None):
        if planId is None:
            return self._getBasic("plan")
        else:
            return self._getBasic("plan/%s" % planId)

    def getPlans(self):
        return self._getBasic("plans")

    def getService(self, serviceId = None):
        if serviceId is None:
            return self._getBasic("service")
        else:
            return self._getBasic("service/%s" % serviceId)

    def getServices(self):
        return self._getBasic("services")

    def getContacts(self):
        return self._getBasic("contacts")

    def getFriends(self):
        return self._getBasic("friends")

    def printMyInfo(self):
        usage = self.getUsage()
        inMB = 1024 * 1024
        endTime = datetime.datetime.fromtimestamp(usage["endTime"] / 1000) 
        delta = endTime - datetime.datetime.now()
        print "Data used: %0.2f%% (%0.2f MB of %0.2f MB) Time until quota reset: %d days %d hours (%s)" % (usage["percentUsed"] * 100, usage["planLimitUsed"] / inMB, usage["totalLimit"] / inMB, delta.days, delta.seconds / 3600, endTime )


def run(username, password):
    fp = FreedomPop(username, password)
    fp.printMyInfo()
    """
    Full list of methods:
    fp.getUsage()       # get the data usage, begin/end quota period, quota MB bonuses.
    fp.getPlan()        # get current plan
    fp.getPlans()       # list of available plans
    fp.getService()     # get current subscribed service
    fp.getServices()    # list of available services
    fp.getInfo()        # get the account's first/last name, last login time, email address
    fp.getFriends()     # list of people friended this account
    fp.Contacts()       # I'm not sure what this for
    # there are some other API that can update/write to your account that I reluctant to expose it here...
    
    """

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: python api.py <username> <password>"
        sys.exit()

    run(sys.argv[1], sys.argv[2]) 


