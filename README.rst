Tumblr Image Download Script
----------------------------

| |Build Status| |codecov| |Code Climate|

Description
^^^^^^^^^^^

| This is a fork of `leyle's
  tumblr\_imgs\_download <https://github.com/leyle/tumblr_imgs_download>`__
| for python3 that allows for a list of blogs to be specified in a text
  file
| as well as command line options for toggling threading and other
  features.
| It downloads all images posted or reblogged by the users specified in
  blogs.txt
| (or the specified file).

Features
^^^^^^^^

-  List Multiple Blogs in text file (no need to edit code)
-  Tag support to only grab certain content
-  Optional Multi-Threaded Downloading
-  Optional Download Streaming
-  Optional Download Timeout
-  Optional Proxy use

Dependant Libraries
^^^^^^^^^^^^^^^^^^^

-  requests

Usage
^^^^^

Parameters
''''''''''

::

 tumblr-ids [-h] [-i] [-s] [-t] [-n TIMEOUT] [-f FILENAME] [-p PROXY]
            [--tumblr-input TUMBLR] [-l LIMIT]

 optional arguments:
  -h, --help            show this help message and exit
  -i, --noinfo          Doesn't show blog list or ask for confirmation
  -s, --stream          Files downloaded are streamed
  -t, --threading       Download using threading
  -n TIMEOUT, --timeout TIMEOUT
                        Specify download timeout in seconds (Default is none)
  -f FILENAME, --filename FILENAME
                        Specify alternate filename for blogs.txt
  -p PROXY, --proxy PROXY
                        Specify proxy in the form 'protocol://host:port'
  --tumblr-input TUMBLR
                        Tumblr user input.
  -l LIMIT, --limit LIMIT
                        Limit the download image.

blogs.txt
'''''''''

| By default the script will search for a file called blogs.txt in the
  folder
| which lists out all blogs to be downloaded from.
| The format for this file is as follows:

-  ``#`` used for comments
-  ``--`` used to skip blog
-  List blogs one per line as:
-  Username (secondary domain) ``lazy-artist``
-  URL ``http://cool-artist.tumblr.com/``
-  Any other URL form
   ``http://www.cool-artist.tumblr.com/post/cool-art-post.html``
   or ``cool-artist.tumblr.com/post/cool-art-post.html``
-  ``;;`` used after blog url to specify tags to download from.
-  seperate tags with ``,``

Example file:

::

    #This line is a comment
    #Use -- to skip blogs:
    --http://inactive-artist.tumblr.com/

    #Blogs can be listed in Username format or URL format

    #Username Format
    lazy-artist

    #URL Format
    http://cool-artist.tumblr.com/

    #TAG Format
    http://reblogging-artist.tumblr.com/;;original-post,cute

    #If used, this file will try to download from "cool-artist", "lazy-artist" and "reblogging-artist",
    #but not "inactive-artist"
    #From "reblogging-artist", it will only download posts tagged "original-post" or "cute"
    #(Helpful for filtering out blogs that reblog a lot but have a tag for their original content)

Todo
^^^^

-  add back support for url extraction

.. |Build Status| image:: https://travis-ci.org/rachmadaniHaryono/tumblr_image_download_script.svg?branch=master
   :target: https://travis-ci.org/rachmadaniHaryono/tumblr_image_download_script
.. |codecov| image:: https://codecov.io/gh/rachmadaniHaryono/tumblr_image_download_script/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/rachmadaniHaryono/tumblr_image_download_script
.. |Code Climate| image:: https://codeclimate.com/github/rachmadaniHaryono/tumblr_image_download_script/badges/gpa.svg
   :target: https://codeclimate.com/github/rachmadaniHaryono/tumblr_image_download_script
