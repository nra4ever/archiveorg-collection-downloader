Batch downloads documents in a given collection from archive.org.

###Note: this script requires the python libraries Requests and clint to be installed, to do so, run the command below
```shell
pip install requests clint
```

Examples:
```shell
#Download issues of American Woodworker to the current directory (the default)
python3 download.py --collection=americanwoodworker

#Download issues of Today's Woodworker to /home/justif/todays-woodworker in epub
python3 download.py --collection=todayswoodworker --format=epub --destination=~/todays-woodworker
```
This hasn't been tested on any collections other than the above, but it should work.  You might see errors if some files aren't available in the requested format.
