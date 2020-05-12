# NookazonPoster
A simple python script to manage Nookazon postings.

```
usage: Nookazon.py [-h] [-a] [-du] [-do] [-d] [-p MINUTES]

Handle Nookazon listings.

optional arguments:
  -h, --help            show this help message and exit
  -a, --add, --add-listings
                        Will list all the items defined in the _listings variable to the user's profile.
  -du, --dump, --dump-listings
                        Will dump all listings AFTER deleting/creating listings.
  -do, --dump-old, --dump-old-listings
                        Will dump all listings BEFORE deleting/creating listings.
  -d, --delete, --delete-listings
                        Will delete all postings in the user's profile.
  -p MINUTES, --periodically MINUTES, --periodically-list MINUTES
                        If this is set, it will re-post all listings every N minutes.
```
