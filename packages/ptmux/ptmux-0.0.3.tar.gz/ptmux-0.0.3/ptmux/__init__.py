import os
import sys
import time
import libtmux
import contextlib
import copy
import typing

class tmuxhandler(object):
    def __init__(self, session_name:str, time_to_wait:int=0, display:bool=False, base_pane:typing.Optional[int]=None, base_window:typing.Optional[int]=None):
        self.session_name = session_name
        if self.session_name is not None:
            for session in libtmux.Server().list_sessions():
                if session.name == self.session_name:
                    self.session = session
                    break
        if self.session is None:
            self.session = libtmux.Server().new_session(session_name=self.session_name)

        self.time_to_wait = time_to_wait
        self.display = display
        self._pane = pane
        self._window = window
        self._history = []

    def wait():
        if self.time_to_wait != 0:
            if display:print("[", end='', flush=True)
            for _ in range(self.time_to_wait):
                if display:print(".", end='', flush=True)
                time.sleep(1)
            if display:print("]", flush=True)

    @property
    def window(self):
        return self.session.list_windows()[self._window or 0]

    @property
    def pane(self):
        return self.window.list_panes()[self._pane or 0]

    def send(self, content:str, enter:bool=False):
        content = content.strip()

        self._history += [content]
        self.pane.send_keys(content, enter=enter)

        self.wait()

    def recieve(self) -> str:
        return self(self.pane.cmd("capture-pane", "-p").stdout)

    def contains(self, string)->bool:
        return string in self.recieve()

    def __call__(self, content:str, enter:bool=False, clear:bool=False):
        if self.clear:self.clear()
        self.send(content,enter=enter)
        return self.recieve()

    def rmatch(self, string)->bool:
        import re
        return re.search(string, self.recieve())

    def clear(self):
        self.pane.clear()

    def __enter__(self):
        return self

    def __exit__(self, a=None, b=None, c=None):
        if self.session_name is not None:
            try:
                libtmux.Server().kill_session(target_session=self.session_name)
                self.session = None
            except:pass

    @contextlib.contextmanager
    def via_settings(self, window:int, pane:int):
        original_window = copy.deepcopy(self._window)
        original_pane = copy.deepcopy(self._pane)
        try:
            yield
        finally:
            self._window = original_window
            self._pane = original_pane