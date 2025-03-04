import os
try:
	import requests,random,string,re,json
except:
	os.system("pip install requests")


def youtube_downlad(Link:str):
	if Link.startswith('https://www.youtube.com/watch?v='):
		url = "https://www.youtube.com/youtubei/v1/player"
		#print(Link.split('.com')[1])
		params = {
      'prettyPrint': "false",
      'key': "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    }
		payload = {
      "contentCheckOk": True,
      "attestationRequest": {
        "omitBotguardData": True
      },
      "playbackContext": {
        "contentPlaybackContext": {
          "html5Preference": "HTML5_PREF_WANTS",
          "vis": 0,
          "referer": Link,
          "currentUrl": Link.split('.com')[1],
          "playerWidthPixels": 640,
          "autonavState": "STATE_ON",
          "lactMilliseconds": "-1",
          "playerHeightPixels": 360,
          "splay": False,
          "signatureTimestamp": "20145"
        }
      },
      "racyCheckOk": True,
      "context": {
        "request": {
          "internalExperimentFlags": [],
          "useSsl": True
        },
        "client": {
          "utcOffsetMinutes": 180,
          "osVersion": "17.5.1.21F90",
          "hl": "en",
          "clientName": "IOS",
          "gl": "IQ",
          "deviceMake": "Apple",
          "deviceModel": "iPhone16,2",
          "userAgent": "com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)",
          "clientVersion": "19.29.1",
          "osName": "iPhone",
          "visitorData": "CgsxWWV3R2taeklnZyiF8JG-BjIKCgJJURIEGgAgFw%3D%3D"
        }
      },
      "videoId": Link.split('watch?v=')[1]
    }
		devices = ["Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QP1A.190711.020)","Mozilla/5.0 (Linux; Android 11; SM-G960F Build/RQ3A.210801.001)","Mozilla/5.0 (Linux; Android 9; Galaxy S9 Build/PPR1.180610.011)"]
		platforms = [
            "Android 10", "Android 11", "Android 12", "Android 13"
        ]
		device = random.choice(devices)
		platform = random.choice(platforms)
		user_agent = f"Mozilla/5.0 (Linux; {platform}; {device.split(' ')[3]} Build/{device.split(' ')[-1]}) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36 YouTube/16.10.35"
		headers = {
      'User-Agent': user_agent,
    #  'Accept-Encoding': "br,gzip",
      'Content-Type': "application/json",
      'referer': Link,
      'sec-fetch-dest': "empty",
      'sec-fetch-mode': "same-origin",
      'sec-fetch-site': "same-origin",
      'x-youtube-client-name': "5",
      'x-youtube-client-version': "19.29.1",
      'x-youtube-sts': "20145",
      'x-youtube-utc-offset': "180",
      'origin': "https://www.youtube.com",
      'x-origin': "https://www.youtube.com",
      'x-goog-visitor-id': "CgsxWWV3R2taeklnZyiF8JG-BjIKCgJJURIEGgAgFw%3D%3D",
      'accept-language': "en,en-US;q=0.8,en;q=0.6",
      'content-type': "application/json; charset=utf-8",
      'Cookie': "VISITOR_INFO1_LIVE=1YewGkZzIgg; YSC=Cc6w1pD_kJU; CONSENT=YES+511; __Secure-ROLLOUT_TOKEN=CPrSp4yi0cC57QEQp52Xg9rriwMYp52Xg9rriwM%3D; VISITOR_PRIVACY_METADATA=CgJJURIEGgAgFw%3D%3D; SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjQwODExLjA4X3AwGgJlbiACGgYIgIr1tQY; GPS=1"
    }
		response = requests.post(url, params=params, data=json.dumps(payload), headers=headers)
		rr =re.findall('"adaptiveFormats":([^>]+)',response.text)
		rrln = json.loads(json.dumps(rr[0]))
		uiv = re.findall('"url":"([^"]+)","mimeType"',rrln)
		uia = re.findall('"mimeType":"([^"]+)',rrln)#"mimeType": "audio/mp4
		uiaa = re.findall('"url":"([^"]+)","mimeType"',rrln)
		da=uiaa[-1]
		dv = uiv[1]
		return {'audio':da , 'video':dv}

print(youtube_downlad('https://www.youtube.com/watch?v=v9Uu-5ysu4w'))

	


 