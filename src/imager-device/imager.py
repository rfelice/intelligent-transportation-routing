import pycurl
import certifi
import ibmiotf.device
import cStringIO
import time
from picamera import PiCamera

# Watson VR response is stored here
response = cStringIO.StringIO()   

filename = "image.jpg"
    
c = pycurl.Curl()
# set watson visual recognition url
c.setopt(c.URL, 'https://gateway-a.watsonplatform.net/visual-recognition/api/v3/detect_faces?api_key=1fa7d37bb00f3789429180b7954458b8cb5dd566&version=2016-05-20')
# get updated certs
c.setopt(pycurl.CAINFO, certifi.where())
# save the server response for post to node
c.setopt(c.WRITEFUNCTION, response.write)
c.setopt(c.HTTPPOST, [
    ('fileupload', (
        # upload the contents of this file
        c.FORM_FILE, filename,
        # specify a different content type
        c.FORM_CONTENTTYPE, 'image/jpeg',
    )),
])


organization = "prwacl"
deviceType = "imager"
deviceId = "busstop2"
authMethod = "token"
authToken = "busstop2AuthT0ken"

# Initialize the device client.
try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

#Image related variables
deviceId = None
imgUploadServer = None
PIC_INTERVAL = None
imgResolution = "320x240" #Image resolution
app_key = None
camera = PiCamera()
camera.resolution = (320, 240)

def takePic() :
    global imgResolution
    
    filename = "image.jpg"
        
    camera.start_preview()
    time.sleep(2)    
    camera.capture(filename)
    time.sleep(1)
    camera.stop_preview()

# Connect to IoTP
deviceCli.connect()

while True:
	# taken image
	takePic()
	
	#post image to watson visual recognition
	c.perform()
	c.close()
	data = response.getvalue()
#	data = '{    "images": [        {            "faces": [                {                    "age": {                        "max": 24,                        "min": 18,                        "score": 0.413116                    },                    "face_location": {                        "height": 88,                        "left": 29,                        "top": 0,                        "width": 64                    },                    "gender": {                        "gender": "MALE",                        "score": 0.0109869                    }                }            ],            "image": "image.jpg"        }    ],    "images_processed": 1}'

	# post watson response to Node
	success = deviceCli.publishEvent("busstop2", "json", data)
	time.sleep(15)

deviceCli.disconnect()