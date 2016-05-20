## Tumblr Image Download Script

#### Description
This is a fork of leyle's tumblr_imgs_download that allows for a list of blogs to be specified in a text file as well as command line options for toggling threading and other features. It downloads all images posted or reblogged by the users specified in blogs.txt (or the specified file).

#### Features
- List Multiple Blogs in text file (no need to edit code)
- Optional Multi-Threaded Downloading
- Optional Download Streaming
- Optional Download Timeout

#### Dependant Libraries
- requests

#### Usage

##### Parameters
```
-i, --noinfo          Doesn't show blog list or ask for confirmation
-s, --stream          Files downloaded are streamed
-t, --threading       Download using threading
-n <TIMEOUT>, --timeout <TIMEOUT>
                      Specify download timeout in seconds (Default is none)
-f FILENAME, --filename FILENAME
                      Specify alternate filename for blogs.txt
```

##### blogs.txt
By default the script will search for a file called blogs.txt in the folder which lists out all blogs to be downloaded from. The format for this file is as follows:
- # used for comments
- -- used to skip blog
- List blogs one per line as 
  - Username (secondary domain) "lazy-artist"
  - URL "http://cool-artist.tumblr.com/"
  - Any other URL form "http://www.cool-artist.tumblr.com/post/cool-art-post.html" or "cool-artist.tumblr.com/post/cool-art-post.html"

Example file:
```
#This line is a comment
#Use -- to skip blogs:
--http://inactive-artist.tumblr.com/

#Blogs can be listed in Username format or URL format

#Username Format
lazy-artist

#URL Format
http://cool-artist.tumblr.com/

#If used, this file will try to download from "cool-artist" and "lazy-artist" but not "inactive-artist"
```

#### Todo
- add back support for url extraction
- add back support for proxy
