
# Image Authentication SDK from MyDesign99

Use the Image Authentication SDK from MyDesign99 on your server to build fully formatted URL's for your MyDesign99 images.

> **To be used on your Python or Django server**

## Example

Suppose you have a server that maintains a database of high school student grades. You can pass a StudentID to your server, calculate the student's grade average, and return a full URL for the grade and the correct data graphic. Your own data graphics are called "assets" on MyDesign99.

```
studentID = routeParams[0]
publicKey = config.getConfig("public_key")
secretKey = config.getConfig("secret_key")
score     = database.getStudentScore(studentID)		# some database funtion on your server
assetName = "radial-wedges"

# call the MD99 SDK
imageUrl = md99authtoken.processAll (publicKey, secretKey, score, assetName)
```

## Use in conjunction with our Python Server Demo (md99demo)

The MyDesign99 Python server demo (md99demo) responds to 2 different URLS to create an authenticated MD99 image URL. URL #1 contains the "value" and "asset_name" in the full URL. URL #2 uses POST parameters "value" and "asset_name". 

The demo uses this SDK package to communicate with the MyDesign99 servers. 

## USAGE

>Before using this SDK, the python developer needs to request a "demo" pair of public/secret keys or use the public/secret keys associated with an existing MyDesign99 account.

There are 4 function in this SDK package.

```
getMD99AuthToken (publicKey, secretKey)
createImageURL   (clientID, token, value, assetName)
errorImageURL    ()
processAll       (publicKey, secretKey, value, assetName)
```

getMD99AuthToken (publicKey, secretKey)
> Request the current authentication token. The developer's public and secret keys are required.

createImageURL (clientID, token, value, assetName)
> Create a well-formed URL for the requested image. "clientID" is the publicKey. "token" is retrieved using the "getMD99AuthToken" function. "value" is the numeric value to be displayed in the MD99 graphic. "assetName" is the name of the developer's MD99 asset (graphic) to be displayed.

errorImageURL ()
> Create a well-formed URL for the standard MD99 error image.

processAll (publicKey, secretKey, value, assetName)
> Request the current authentication token and return the well-formed image URL. In case of an error, the Error Image URL is returned.


## Installation

To install this Python package:

```
pip install md99authtoken
```

To use it in a Python script or interactive shell:

```
from md99authtoken import md99authtoken
```


