import csv
import xmljson
import json
from lxml.etree import fromstring, tostring

with open('windirs.txt','r') as tsv_file:
    #- Ref: https://stackoverflow.com/questions/14158868/python-skip-comment-lines-marked-with-in-csv-dictreader
    read_tsv = csv.reader(filter(lambda row: row[0]!='#', tsv_file),delimiter="\t")

    for lines in read_tsv:
        img_offset=lines[0]
        file_name=lines[1]
        file_xml=lines[2]
        #print(file_name)
        #print(file_xml)

        #- Ref: https://stackoverflow.com/questions/191536/converting-xml-to-json-using-python
        file_json=json.dumps(xmljson.parker.data(fromstring(file_xml)))
        file_dict=json.loads(file_json)
        #print(file_dict)


        '''
            {
            "atime_fn": "2019-10-27T05:53:22Z",
            "atime_si": "2020-05-23T03:51:15Z",
            "attr_flags": 268435456,
            "crtime_fn": "2019-10-27T05:53:22Z",
            "crtime_si": "2019-10-27T05:53:22Z",
            "ctime_fn": "2019-10-27T05:53:22Z",
            "ctime_si": "2020-05-23T03:51:15Z",
            "filename": "WindowsForm0b574481#",
            "filesize": 1000000000000,
            "filesize_alloc": 0,
            "lsn": 355952237778,
            "mtime_fn": "2019-10-27T05:53:22Z",
            "mtime_si": "2020-05-23T03:51:15Z",
            "nlink": 2,
            "par_ref": 3241696,
            "par_seq": 4,
            "seq": 2
            }

            Looking at the above struct:
            (M) - mtime is the DATA Modification Time
            (A) - atime is the Access Time
            (C) - ctime is the Metadata Modification Time
            (B) - crtime is the Creation Time/Birth Time

        '''
        try:
            out_file_name=file_dict['filename']
        except KeyError:
            out_file_name="NOFILENAME"

        try:
            out_file_birth=file_dict['crtime_fn']
        except KeyError:
            out_file_birth='1600-01-01T00:00:00Z'

        try:
            out_file_modified=file_dict['mtime_si']
        except KeyError:
            out_file_modified='1600-01-01T00:00:00Z'

        try:
            out_file_lsn=file_dict['lsn']
        except KeyError:
            out_file_lsn=0


        print(out_file_name,"|",out_file_birth,"|",out_file_modified,"|",out_file_lsn)
