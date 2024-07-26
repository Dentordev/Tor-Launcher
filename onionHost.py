"""Used to easily host and launch onionsites up without the bullshit"""
from stem.control import Controller
from stem.process import launch_tor_with_config
from typing_extensions import ParamSpec, Callable, TypeVar
from typing import Optional
import pathlib
import sys
import os
import logging


__version__ = "0.1.1"


# Framework was inspried by torrequest but for making things easier to configure tor hidden services with...
# TODO: Add Custom tor.exe param for those with custom enviornment variables.
class Tor:
    """Inspired by torrequest and is used to host hidden services with ease..."""

    def __init__(
        self,
        proxy_port: int = 9050,
        ctrl_port: int = 9051,
        password: Optional[str] = None,
        log:bool = False
    ):
        self.log = log
        self.proxy_port = proxy_port
        self.ctrl_port = ctrl_port

        self._tor_proc = None
        if not self._tor_process_exists():
            self._tor_proc = self._launch_tor()

        self.ctrl = Controller.from_port(port=self.ctrl_port)
        self.ctrl.authenticate(password=password)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.close()

    def host_hidden_service(
        self, port: int, host: str = "127.0.0.1", hs_dir: str = None, ssl_port:Optional[int] = None
    ) -> str:
        """Sets a hidden service to be hosted, returns with the host's name by default..."""
        if not hs_dir:
            hs_dir = os.path.join(os.getcwd(), ".hidden-service")
            if not os.path.exists(hs_dir):
                os.mkdir(".hidden-service")
        if sys.platform == "win32":
            # Tor has problems parsing normal directories given with "\\" <- this string...
            hs_dir = pathlib.Path(hs_dir).as_posix()

        args = [
                ("HiddenServiceDir", hs_dir),
                ("HiddenServicePort", "80 %s:%s" % (host, str(port))),
            ]
        if ssl_port:
            args.append(
                ("HiddenServicePort", "443 %s:%s" % (host, str(ssl_port)))
            )
        if self.log:
            logging.debug("Lauching Tor Hidden Service On %s", args)
        self.ctrl.set_options(args)
        return open(hs_dir + "/hostname", "r").read().strip()

    def _tor_process_exists(self):
        try:
            ctrl = Controller.from_port(port=self.ctrl_port)
            ctrl.close()
            return True
        except:
            return False

    def _launch_tor(self):
        return launch_tor_with_config(
            config={
                "SocksPort": str(self.proxy_port),
                "ControlPort": str(self.ctrl_port),
            },
            take_ownership=True,
        )

    def close(self):
        try:
            self.ctrl.close()
        except:
            pass
        if self._tor_proc:
            self._tor_proc.terminate()



P = ParamSpec("P")
T = TypeVar("T")

def on_launch(
    port: int = 6669,
    host: str = "127.0.0.1",
    hs_dir:Optional[str] = None,
    proxy_port: int = 9050,
    ctrl_port: int = 9051,
    password: Optional[str] = None,
    show_host: Optional[Callable[[str], None]] = None,
    ssl_port:Optional[int] = None  
):
    """
    Used as a wrapper to tor when launching an onionsite
    This wrapper should be ran before a site gets launched
    such as `starlette` , `fastapi` , `aiohttp` or `flask`, etc...

    Built mainly for being used to workaround server lifespans.

    ## WARNING
    
    This is only useful if we are going to be only
    playing with `one` host.


    ::

        from aiohttp import web 

        route = web.RoutTableDef()
        # fill out what you need...
        ...        

        @on_launch(port=2000)
        def main():
            app = web.Application()
            app.add_routes(route)
            web.run_app(app, port=2000)
        

    """

    def wrapper(func: Callable[P, T]) ->  Callable[P, T]:
        def function(*args, **kwargs):
            with Tor(proxy_port=proxy_port, ctrl_port=ctrl_port, password=password) as tor:
                _host_ = tor.host_hidden_service(port=port, host=host, hs_dir=hs_dir, ssl_port=ssl_port)
                if show_host:
                    show_host(_host_)
                ret = func(*args, **kwargs)
            return ret
        return function
    return wrapper

