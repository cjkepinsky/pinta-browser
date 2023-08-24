# pinta-browser
This repo shows stages of creating my own browser with Python. Pinta comes from The Pinta Island tortoise, 
an extinct subspecies of Galápagos tortoise native to Ecuador's Pinta Island. 
See more here: https://en.wikipedia.org/wiki/Pinta_Island_tortoise.
## Main Features
The idea is inspired by the Arc Browser (https://arc.net/) and my need to switch from MacOS to Linux on which 
this browser is not available. The main features I want to have are:
- split view: several tabs opened in parallel (side-by-side)
- integrated bookmarks/tabs sidebar
  - autosaving all changes to json file
  - sidebar spaces
  - pinned bookmarks
  - easy to CRUD bookmarks
- firefox/chrome plugins 
- free forever
## Pre-Alpha
The browser is in deep pre-alpha stage, it is possible that I will switch to different engine (currently QtWebEngine is used). 
Tested on MacOS Ventura 13.5 (22G74) only with Python 3.9.13.
## Installation and usage
`pipenv install`

`pipenv shell`

`python ./pintaXX.py`

XX - chosen version number of the browser.
