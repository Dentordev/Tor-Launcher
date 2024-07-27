# Tor Launcher
A Small Python Script to help and aid in Launching a tor hidden service all in one script without the bs involved. You are free to copy and paste this code as you wish. 
stem is the only python package that is required. I have handled all the annoyances involved with hosting that had my head bashing against my own keyboard.

# Examples
This will work with aiohttp, flask, fastapi and starlette easily and pretty much any python server application under the sun as the process is being launched before the server is to be ran 
as so the process closes after the server closes which allows for propper cleanup.

```python
# An example with aiohttp inspired by https://stem.torproject.org/tutorials/over_the_river.html

from onionHost import on_launch
from aiohttp import web 
import sys 


route = web.RouteTableDef()

# Allow me to bring in stem's classic example on how to do this
@route.get("/")
async def hiGrandma(request:web.Request):
    return web.Response(body=b"<html><body><h1>Hi Grandma</h1></body></html>", content_type="text/html")


# NOTE: on_launch assumes you have tor.exe setup as an enviornment variable. This is not hard to setup 
# You just need to install tor or the tor-expert-bundle beforehand on either linux , Apple or Windows and then
# setup the enviornment variable to your tor.exe file, from there, let the small and extremely useful on_launch()
# decorator handle the rest...


# NOTE: Remeber that your ports need to match in order to sucessfully host your tor hidden services
@on_launch(port=2000)
def main():
    app = web.Application()
    app.add_routes(route)
    web.run_app(app, port=2000)



if __name__ == "__main__":
    # if you need to use uvloop, install it beforehand otherwise use winloop 
    # it will incease the speed of your server especially on tor.
    if sys.platform != "win32":
        import uvloop; uvloop.install()
    else:
        import winloop; winloop.install()
    
    main()
```


## Hosting Multiple onionsites 
 Hosting Multiple onionsites on a single Python Script Made easy because believe me it's annoying and don't get me started with fixing windows Paths. 
 
```python
from onionHost import Tor
def launch_multiple_onionsites():
    with Tor() as tor:
        tor.host_hidden_service(port=6069, hs_dir="/dir-1")
        tor.host_hidden_service(port=8000, hs_dir="/dir-2")
        # run what you need to below this line remember that when the tor context manager exits so does it's process...
        ...
```


 ## Requirements
- python 3 (I think 3.6 or higher is required here)
- install stem
- install either  [Tor Browser](https://www.torproject.org/download/) or [Tor Expert Bundle](https://dist.torproject.org/torbrowser)
- set up `tor` as an eviornment varaible so that it can be invoked as a command



