#!/usr/bin/python

'''
 * Author: Ramprasad Ramshankar 
 * Alias: diyinfosec
 * Date: 10-Dec-2018
 * Purpose: To read a file of md5 hashes and query for detections in VirusTotal. Requires private API key to avoid throttling the 4 requests per second limit. 
 * Language:  Python
'''

import requests

#- Input file name with list of hashes. A good candidate for this would be the Bro (Zeek) file.log
#- For more info on file.log check: https://corelight.blog/2017/09/15/another-cool-thing-about-bro-tracking-files/
file_name='bro_file_hashes.csv'

#- Open the Input file and iterate through each md5 hash
with open(file_name) as input_md5:
	for items in input_md5:
		params = {'apikey': '<--- Your API Key Here --->', 'resource': items.strip()}

		headers = {"Accept-Encoding": "gzip, deflate", "User-Agent" : "Test user agent"}

		#- Reference: https://www.virustotal.com/en/documentation/private-api/#get-report
		response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params, headers=headers)
		json_response = response.json()
		try:
		    if json_response:
					detection_count=json_response.get('positives')
					#- If a file downloaded in our environment is being detected by more than 5 AV engines then flag it.
					if detection_count >= 5:
						print "Detected"
						print input_md5
						print items.strip(), ",", detection_count
		except:
		    print 'Err'
