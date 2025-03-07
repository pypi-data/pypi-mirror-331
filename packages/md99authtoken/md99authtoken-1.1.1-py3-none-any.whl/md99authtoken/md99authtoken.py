from . import md99utils
import logging
from urllib import request, parse

#gRemoteDomain   = "https://mydesign99.com/"
gRemoteDomain   = "https://jmc2.lakeshoresoftwareinc.com/"
gAuthTokenRoute = "api/get/authtoken"
gErrImg         = "images/image_not_found.png"

# ------- Function: main entry point into this module -----------
def getMD99AuthToken (publicKey, secretKey):
    storedToken = md99utils.readTokenDataFromFile ()
    if not storedToken == None:
        #print ("<br />Found Token in Local file<br />")
        return storedToken

    #print ("<br />No token found in Local file<br />")
    
    payloadAr   = {'client_id': publicKey}
    fullJwt     = md99utils.buildJWT (payloadAr, secretKey)
    postParams  = {'jwt': fullJwt}
    encodedData = parse.urlencode (postParams).encode()
    
    remoteUrl   = gRemoteDomain + gAuthTokenRoute
    
    fullReq     = request.Request (remoteUrl, encodedData)
    
    #print ("<br />*** md99 *** Ready to make http request: " + remoteUrl)
    
    reply       = request.urlopen (fullReq)
    charset     = reply.info().get_content_charset()
    content     = reply.read().decode(charset)
    
    token, errMsg = md99utils.parseTokenFromResult (content)
    if token == None:
        logging.error (errMsg);
        
    return token

# ------- Function: main entry point into this module -----------
def createImageURL (clientID, token, value, assetName):
    if type(clientID) != 'str':
        clientID = str (clientID)
    if type(token) != 'str':
        token = str (token)
    if type(value) != 'str':
        value = str (value)
    if type(assetName) != 'str':
        assetName = str (assetName)
        
    assetName = md99utils.stripAssetName (assetName)
    
    imgUrl = gRemoteDomain + "get/" + clientID + "/" + token + "/" + value + "/" + assetName + ".png"
    return imgUrl

# ------- Function: main entry point into this module -----------
def errorImageURL ():
    return gRemoteDomain + gErrImg
    
# ------- Function: main entry point into this module -----------
def processAll (publicKey, secretKey, value, assetName):
    token = getMD99AuthToken (publicKey, secretKey)
    if token == None:
        return errorImageURL ()
    
    return createImageURL (publicKey, token, value, assetName)