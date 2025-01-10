"""Try to run all the documentation examples with runpy and check they don't raise
exceptions.
"""

import os
import pathlib
import runpy
import shutil
from contextlib import contextmanager

import pytest

from moviepy.tools import no_display_available


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


# Dir for doc code examples to run
DOC_EXAMPLES_DIR = "docs/_static/code"

# List of examples script to ignore, mostly scripts that are too long
DOC_EXAMPLES_IGNORE = ["trailer.py", "display_in_notebook.py"]

# If no display, also remove all examples using preview
if no_display_available():
    DOC_EXAMPLES_IGNORE.append("preview.py")

scripts = list(pathlib.Path(DOC_EXAMPLES_DIR).resolve().rglob("*.py"))
scripts = dict(zip(map(str, scripts), scripts))  # This make test name more readable


@pytest.mark.parametrize("script", scripts)
def test_doc_examples(util, tmp_path, script):
    if os.path.basename(script) == "preview.py":
        pytest.skip("Skipping preview.py because no display is available")
    print("Try script: ", script)

    if os.path.basename(script) in DOC_EXAMPLES_IGNORE:
        return

    # Lets build a test dir with all medias needed to run our test in
    shutil.copytree(util.DOC_EXAMPLES_MEDIAS_DIR, os.path.join(tmp_path, "doc_tests"))
    test_dir = os.path.join(tmp_path, "doc_tests")

    with cwd(test_dir):
        runpy.run_path(script)


if __name__ == "__main__":
    pytest.main()
