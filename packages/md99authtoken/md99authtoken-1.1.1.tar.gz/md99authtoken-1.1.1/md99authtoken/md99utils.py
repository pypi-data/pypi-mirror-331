import base64
import json
import hmac
import hashlib
import re
import os.path
import time
import logging

# ------- Function: process the reply from the remote server -----------
def parseTokenFromResult (replyJson):
    #print ("<br />JSON reply from server<br />")
    #print (replyJson)
    
    try:
        replyArray = json.loads (replyJson)
    except:
        return None, "Could not process the reply (invalid json)"

    if 'is_success' not in replyArray:
        return None, "Could not process the reply (missing success)"
        
    if replyArray['is_success'] != '1'  and  replyArray['is_success'] != 1:
        if 'err_msg' not in replyArray:
            return None, "Could not process the reply (missing message)"
        return None, "The server returned an error: " + replyArray['err_msg']

    if 'data' not in replyArray:
        return None, "Could not process the reply (missing data)"

    dataArray = replyArray['data']
    if 'token' not in dataArray:
        return None, "Could not process the reply (missing token)"

    token = dataArray['token']

    writeTokenDataToFile (dataArray)
    
    return token, None

# ------- Function: format the Asset Name to be correctly URL encoded -----------
def stripAssetName (name):
    name = name.replace (" " , "-")                 # replace spaces with dashes
    name = name.lower()                             # change to all lower case
    name = re.sub ('[^-a-z0-9_]', '', name)         # keep only dash, underscore, letters and numbers
    #name = re.sub ('\-+', '-', name)               # remove duplicate dashes
    name = re.sub ('-+', '-', name)                 # remove duplicate dashes
    name = name.strip ("-")                         # trim dashes
    
    return name;
# ------- Function: Write JSON array to file as string -----------
def stringifyNoSpaces (srcArray):
    asJsonStr = json.dumps (srcArray)
    return asJsonStr;

# ------- Function: JSON array to string with no spaces -----------
def writeTokenDataToFile (srcArray):
    asJsonStr = json.dumps (srcArray, separators=(',', ':'))
    with open('md99_data.txt', 'w+') as fileObj:
        fileObj.write (asJsonStr)
# ------- Function: JSON array to string with no spaces -----------
def readTokenDataFromFile ():
    if not os.path.exists ('md99_data.txt'):
        return None
    with open ('md99_data.txt', 'r') as fileObj:
        asJsonStr = fileObj.read ()
        if len(asJsonStr) == 0:
            return None
            
        try:
            asArray = json.loads (asJsonStr)
        except:
            #print ("<br />Invalid JSON in cache text file")
            logging.error ("Invalid JSON in cache text file");
            return None
        if 'token' not in asArray:
            return None
        if 'expires' not in asArray:
            return None
        curTime = int(time.time())
        expires = int(asArray['expires'])
        if curTime > expires:
            return None
        return asArray['token']

# ------- Function: standard array converted to a Base64-encoded string -----------
def arrayTo64 (srcAr):
    asJsonStr = stringifyNoSpaces (srcAr)
    asBytes   = bytes (asJsonStr, 'utf-8')
    b64Bytes  = base64.b64encode (asBytes)
    b64Str    = str (b64Bytes.decode ('utf-8'))
    b64Str    = b64Str.replace("+", "-")
    b64Str    = b64Str.replace("/", "_")		
    b64Str    = b64Str.strip ('=');
    return b64Str
# ------- Function -----------
def _64ToArray (_64Str):
    asBytes = base64.b64decode (_64str)
    asJsonStr = asBytes.decode ('utf-8')
    return json.loads (asJsonStr)
# ------- Function: build the full JWT token as a string -----------
def buildJWT (payloadAsAr, secret):
    secret = bytes (secret, 'utf-8')
    hdrAr  = {"alg" : "HS256", "typ" : "JWT"}

    hdr64Str    = arrayTo64 (hdrAr)
    pay64Str    = arrayTo64 (payloadAsAr)
    
    full64Str   = hdr64Str + "." + pay64Str
    full64Bytes = bytes (full64Str, 'utf-8')
    dig = hmac.new (secret, full64Bytes, hashlib.sha256).digest()

    sign64Str = str (base64.b64encode(dig).decode())
    sign64Str = sign64Str.replace("+", "-")
    sign64Str = sign64Str.replace("/", "_")		
    sign64Str = sign64Str.strip ('=');
    
    return hdr64Str + "." + pay64Str + "." + sign64Str