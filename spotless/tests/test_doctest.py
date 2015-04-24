# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flake8 import engine
from hacking.tests import test_doctest
import pkg_resources
import six
import testscenarios


HackingTestCase = test_doctest.HackingTestCase


def load_tests(loader, tests, pattern):

    flake8_style = engine.get_style_guide(parse_argv=False,
                                          # Ignore H104 otherwise it's
                                          # raised on doctests.
                                          ignore=('F', 'H104'))
    options = flake8_style.options

    for entry in pkg_resources.iter_entry_points('flake8.extension'):
        if not entry.module_name.startswith('spotless.'):
            continue
        check = entry.load()
        name = entry.attrs[0]
        if check.skip_on_py3 and six.PY3:
            continue
        for (lineno, (raw, (code, source))) in enumerate(
                test_doctest._get_lines(check)):
            lines = [part.replace(r'\t', '\t') + '\n'
                     for part in source.split(r'\n')]
            test_doctest.file_cases.append(("%s-%s-line-%s"
                                            % (entry.name, name, lineno),
                                            dict(
                                                lines=lines,
                                                raw=raw,
                                                options=options,
                                                code=code)))

    return testscenarios.load_tests_apply_scenarios(loader, tests, pattern)
