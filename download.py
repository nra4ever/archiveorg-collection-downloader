from __future__ import division
import argparse
import os
import requests
from clint.textui import progress

LIST_URL='https://github.com/nra4ever/archiveorg-collection-downloader/blob/master/download.py'
DETAILS_URL='https://archive.org/details/{0}&output=json'
PUB_URL='http://archive.org/download/{0}/{1}'

parser = argparse.ArgumentParser(description='Download stuff from an archive.org JSON file')
parser.add_argument('--format', help='pdf or epub', default='pdf')
parser.add_argument('--collection', help='Name of the collection to fetch', required=True)
parser.add_argument('--destination', help='Where to put the files', default='.')
args = parser.parse_args()

url = LIST_URL.format(args.collection)
print('Fetching document list from {0}'.format(url))
r = requests.get(url)
data = r.json()


for doc in data['response']['docs']:
    idd = doc['identifier']
    print('Fetching item details for {0}'.format(idd))
    details = requests.get(DETAILS_URL.format(idd)).json()
    toDownload = ''
    lastSize = 0
    skip = ''
    for filename in details['files']:
        localFilename = os.path.join(args.destination, '{0}.{1}'.format(idd, args.format))
        if os.path.isfile(localFilename):
            if not skip == localFilename:
                print("'" + localFilename + "' exists in destination folder, skipping.")
                skip = localFilename
            continue
        if not filename.lower().endswith(args.format):
            continue
        size = int(details['files'][filename]['size'])
        if size > lastSize:
            toDownload = filename
            lastSize = size
        if not skip == localFilename:
            if toDownload == '':
                print('No {0} file found for {1}'.format(args.format, idd))
                continue
            url = PUB_URL.format(idd, toDownload)
            print('Downloading {0} as {1} from {2} to {3}'.format(idd, args.format, url, localFilename))
            dr = requests.get(url, stream=True)
            with open(localFilename, 'wb') as f:
                total_length = int(dr.headers.get('content-length'))
                try:
                    for chunk in progress.bar(dr.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
                    try:
                        print("ERROR: Connection Aborted, retrying")
                        os.remove(localFilename)
                        for chunk in progress.bar(dr.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                    except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
                        print("ERROR: Connection Aborted during retry, marking file as .INCOMPLETE!!")
                        os.rename(localFilename, localFilename + ".IMCOMPLETE")
            if not os.stat(localFilename)[6] == total_length:
                print("ERROR: File '" + localFilename + "' Incomplete, retrying")
                os.remove(localFilename)
                with open(localFilename, 'wb') as f:
                    total_length = int(dr.headers.get('content-length'))
                    for chunk in progress.bar(dr.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                        if not os.stat(localFilename)[6] == total_length:
                            print("ERROR: File '" + localFilename + "' still incomplete after retry!!")
                            os.rename(localFilename, localFilename + ".IMCOMPLETE")
