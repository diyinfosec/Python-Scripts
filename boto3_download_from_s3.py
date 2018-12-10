#!/usr/bin/python

'''
 * Author: Ramprasad Ramshankar 
 * Alias: diyinfosec
 * Date: 10-Dec-2018
 * Purpose: Use the Boto3 API to download files from an s3 bucket to a local directory in your computer
 * Language:  Python
'''
from boto3.session import Session

#- Setting up s3 bucket properties
access_key = '<--- S3 Access Key --->'
secret_key = '<--- S3 Secret Key --->'
#- Just the name of the bucket is sufficient, no need to add any prefixes
bucket_name = '<--- Bucket Name e.g. mys3 --->'
region_name = '<--- Region Name e.g. us-east-2 ---> '

#- Setting up local directory properties
local_file_extension='.csv'
local_file_path='/users/myuser/dest_dir/'

#- Tell AWS about wanting to access the s3 bucket:
#- 1. Create a session object using the Access and Secret Keys
#- 2. Create a s3 object by linking the session object to the s3 resource
#- 3. Create a bucket object from the s3 object and specify the name of the bucket
#- Essentially we are doing: Session_Object --> S3_Resource_Object --> Bucket_Object
session_object = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
s3_object = session_object.resource('s3')
bucket_object = s3_object.Bucket(bucket_name)

#- Enumerate the files inside the s3 bucket
for s3_file in bucket_object.objects.all():
		#- Get the s3 file name
		s3_file_name=s3_file.key
		#print(s3_file_name)

		#- Give a local file name that you want for the downloaded file
		local_file_name=local_file_path+s3_file_name+local_file_extension
		#print(local_file_name)

		#- Finally, download the file
		obj = s3_object.Object(bucket_name, s3_file_name).download_file(local_file_name)

#- And we are done!
