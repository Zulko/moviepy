#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
https://github.com/ionelmc/python-nameless/tree/test-matrix-separate-cext

BSD 2-Clause License

Copyright (c) 2019, Ionel Cristian Mărieș. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import subprocess
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join

base_path = dirname(dirname(abspath(__file__)))


def check_call(args):
    print("+", *args)
    subprocess.check_call(args)


def exec_in_env():
    env_path = join(base_path, ".tox", "bootstrap")
    if sys.platform == "win32":
        bin_path = join(env_path, "Scripts")
    else:
        bin_path = join(env_path, "bin")
    if not exists(env_path):
        import subprocess

        print("Making bootstrap env in: {0} ...".format(env_path))
        try:
            check_call([sys.executable, "-m", "venv", env_path])
        except subprocess.CalledProcessError:
            try:
                check_call([sys.executable, "-m", "virtualenv", env_path])
            except subprocess.CalledProcessError:
                check_call(["virtualenv", env_path])
        print("Installing `jinja2` into bootstrap environment...")
        check_call([join(bin_path, "pip"), "install", "jinja2", "tox", "matrix"])
    python_executable = join(bin_path, "python")
    if not os.path.exists(python_executable):
        python_executable += '.exe'

    print("Re-executing with: {0}".format(python_executable))
    print("+ exec", python_executable, __file__, "--no-env")
    os.execv(python_executable, [python_executable, __file__, "--no-env"])


def main():
    import jinja2
    import matrix

    print("Project path: {0}".format(base_path))

    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(base_path, "ci", "templates")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )

    tox_environments = {}
    for (alias, conf) in matrix.from_file(join(base_path, "setup.cfg")).items():
        python = conf["python_versions"]
        deps = conf["dependencies"]
        tox_environments[alias] = {
            "deps": deps.split(),
        }
        if "coverage_flags" in conf:
            cover = {"false": False, "true": True}[conf["coverage_flags"].lower()]
            tox_environments[alias].update(cover=cover)
        if "environment_variables" in conf:
            env_vars = conf["environment_variables"]
            tox_environments[alias].update(env_vars=env_vars.split())

    for name in os.listdir(join("ci", "templates")):
        with open(join(base_path, name), "w") as fh:
            fh.write(jinja.get_template(name).render(tox_environments=tox_environments))
        print("Wrote {}".format(name))
    print("DONE.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--no-env"]:
        main()
    elif not args:
        exec_in_env()
    else:
        print("Unexpected arguments {0}".format(args), file=sys.stderr)
        sys.exit(1)