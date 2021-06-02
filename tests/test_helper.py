"""Define general test helper attributes and utilities."""

import ast
import contextlib
import functools
import http.server
import importlib
import inspect
import io
import pkgutil
import socketserver
import sys
import tempfile
import threading

import numpy as np

from moviepy.video.io.VideoFileClip import VideoFileClip


PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
TMP_DIR = tempfile.gettempdir()  # because tempfile.tempdir is sometimes None

# Arbitrary font used in caption testing.
if sys.platform in ("win32", "cygwin"):
    FONT = "Arial"
    # Even if Windows users install the Liberation fonts, it is called
    # LiberationMono on Windows, so it doesn't help.
else:
    FONT = (
        "Liberation-Mono"  # This is available in the fonts-liberation package on Linux
    )


@functools.lru_cache(maxsize=None)
def get_test_video():
    return VideoFileClip("media/big_buck_bunny_432_433.webm").subclip(0, 1)


@functools.lru_cache(maxsize=None)
def get_stereo_wave(left_freq=440, right_freq=220):
    def make_stereo_frame(t):
        return np.array(
            [np.sin(left_freq * 2 * np.pi * t), np.sin(right_freq * 2 * np.pi * t)]
        ).T.copy(order="C")

    return make_stereo_frame


@functools.lru_cache(maxsize=None)
def get_mono_wave(freq=440):
    def make_mono_frame(t):
        return np.sin(freq * 2 * np.pi * t)

    return make_mono_frame


@contextlib.contextmanager
def static_files_server(port=8000):
    my_server = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
    thread = threading.Thread(target=my_server.serve_forever, daemon=True)
    thread.start()
    yield thread


@functools.lru_cache(maxsize=None)
def get_moviepy_modules():
    """Get all moviepy module names and if each one is a package."""
    response = []
    with contextlib.redirect_stdout(io.StringIO()):
        moviepy_module = importlib.import_module("moviepy")

        modules = pkgutil.walk_packages(
            path=moviepy_module.__path__,
            prefix=moviepy_module.__name__ + ".",
        )

        for importer, modname, ispkg in modules:
            response.append((modname, ispkg))
    return response


def get_functions_with_decorator_defined(code, decorator_name):
    """Get all functions in a code object which have a decorator defined,
    along with the arguments of the function and the decorator.

    Parameters
    ----------

    code : object
      Module or class object from which to retrieve the functions.

    decorator_name : str
      Name of the decorator defined in the functions to search.
    """

    class FunctionsWithDefinedDecoratorExtractor(ast.NodeVisitor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.functions_with_decorator = []

        def generic_visit(self, node):
            if isinstance(node, ast.FunctionDef) and node.decorator_list:
                for dec in node.decorator_list:
                    if not isinstance(dec, ast.Call) or dec.func.id != decorator_name:
                        continue

                    decorator_argument_names = []
                    if isinstance(dec.args, ast.List):
                        for args in dec.args:
                            decorator_argument_names.extend(
                                [e.value for e in args.elts]
                            )
                    else:
                        for args in dec.args:
                            if isinstance(args, (ast.List, ast.Tuple)):
                                decorator_argument_names.extend(
                                    [e.value for e in args.elts]
                                )
                            else:
                                decorator_argument_names.append(args.value)

                    function_argument_names = [arg.arg for arg in node.args.args]
                    for arg in node.args.kwonlyargs:
                        function_argument_names.append(arg.arg)

                    self.functions_with_decorator.append(
                        {
                            "function_name": node.name,
                            "function_arguments": function_argument_names,
                            "decorator_arguments": decorator_argument_names,
                        }
                    )

            ast.NodeVisitor.generic_visit(self, node)

    modtree = ast.parse(inspect.getsource(code))
    visitor = FunctionsWithDefinedDecoratorExtractor()
    visitor.visit(modtree)
    return visitor.functions_with_decorator
