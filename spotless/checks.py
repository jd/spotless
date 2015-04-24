#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import ast

from hacking import core
import six


@core.flake8ext
class StaticmethodChecker(object):
    r"""Check that the method is declared static if it is so.

    Okay: class X(object):\n    def foo(self):\n        return self
    Okay: class X(object):\n    def foo(*args):\n        return args
    Okay: class X(object):\n    @staticmethod\n    def foo():\n        return 1
    Okay: class X(object):\n    @abc.abstractmethod\n    def f(s):\n        1
    SL901: class X(object):\n    def foo():\n        pass
    SL902: class X(object):\n    def foo(self):\n        return 1
    """

    def __init__(self, tree, filename):
        self.tree = tree

    def run(self):
        for stmt in ast.walk(self.tree):
            # Ignore non-class
            if not isinstance(stmt, ast.ClassDef):
                continue

            # If it's a class, iterate over its body member to find methods
            for body_item in stmt.body:
                # Not a method, skip
                if not isinstance(body_item, ast.FunctionDef):
                    continue

                # Check that it has a decorator
                for decorator in body_item.decorator_list:
                    # We hope that nothing is overwriting the
                    # 'staticmethod' name earlier, but that would be a
                    # BAAAAD practice anyway!
                    if (isinstance(decorator, ast.Name)
                       and decorator.id == 'staticmethod'):
                        # It's a static function, it's OK
                        break
                    # If we are on Python < 3 and the method is declared
                    # abstract using ABC, we ignore it as it's impossible to
                    # declare it static, we need the abstractstaticmethod
                    # provided by Python 3 We could return different result
                    # based on the fact we are running Python 3 or not, but
                    # since most projects are hybrid, let's ignore this even on
                    # Python 3 for now.
                    if (isinstance(decorator, ast.Attribute)
                       and decorator.attr == 'abstractmethod'
                       and isinstance(decorator.value, ast.Name)
                       and decorator.value.id == 'abc'):
                        break
                else:
                    try:
                        first_arg = body_item.args.args[0]
                    except IndexError:
                        # Check if it has *args instead
                        if not body_item.args.vararg:
                            yield (
                                body_item.lineno,
                                body_item.col_offset,
                                "SL902: method missing first argument",
                                "SL902",
                            )
                        # Check next method
                        continue
                    for func_stmt in ast.walk(body_item):
                        if six.PY3:
                            if (isinstance(func_stmt, ast.Name)
                               and first_arg.arg == func_stmt.id):
                                # The first argument is used, it's OK
                                break
                        else:
                            if (func_stmt != first_arg
                               and isinstance(func_stmt, ast.Name)
                               and func_stmt.id == first_arg.id):
                                # The first argument is used, it's OK
                                break
                    else:
                        yield (
                            body_item.lineno,
                            body_item.col_offset,
                            "SL901: method should be declared static",
                            "SL901",
                        )
