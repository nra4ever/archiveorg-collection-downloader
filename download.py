from __future__ import division
import argparse
import json
import os
import time
from sys import stderr
from urllib import request

LIST_URL='http://archive.org/advancedsearch.php?q=collection%3A{0}&rows=1000&output=json'
DETAILS_URL='https://archive.org/details/{0}&output=json'
PUB_URL='http://archive.org/download/{0}/{1}'

parser = argparse.ArgumentParser(description='Download stuff from an archive.org JSON file')
parser.add_argument('--format', help='pdf or epub', default='pdf')
parser.add_argument('--collection', help='Name of the collection to fetch', required=True)
parser.add_argument('--destination', help='Where to put the files', default='.')
args = parser.parse_args()

url = LIST_URL.format(args.collection)
print('Fetching document list from {0}'.format(url))
response = request.urlopen(url)
listdata = response.read()
data = json.loads(listdata.decode('UTF-8'))


def reporthook(blocknum, blocksize, totalsize):
    global start_time
    if blocknum == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        progress_size = int(blocknum * blocksize)
        speed = int(progress_size / (1024 * duration))
        s = "\r%5.1f%% %*d / %d \t %d KB/" % (
            percent, len(str(totalsize)), readsofar, totalsize, speed)
        stderr.write(s)
        if readsofar >= totalsize:
            stderr.write("\n")
    else:
        stderr.write("read %d\n" % (readsofar,))

for doc in data['response']['docs']:
    idd = doc['identifier']
    print('Fetching item details for {0}'.format(idd))
    details = json.loads(request.urlopen(DETAILS_URL.format(idd)).read().decode('UTF-8'))
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
        request.urlretrieve(url, localFilename, reporthook)
        
