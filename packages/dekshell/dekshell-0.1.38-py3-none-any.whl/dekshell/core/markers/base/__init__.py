import os
import re
import shlex
import functools
from dektools.str import deep_format
from dektools.common import classproperty
from dektools.shell import shell_output, shell_exitcode
from ....utils.serializer import serializer
from ....utils.cmd import cmd2ak


class MarkerBase:
    tag_head = None
    tag_tail = None
    branch_set = set()

    var_name_anonymous = '_'

    trans_marker_command_output = '>>'
    trans_marker_command_rc = '>'
    trans_marker_decode = '//'
    trans_marker_encode = '/'
    trans_marker_env = '$'
    trans_marker_eval = '='

    trans_marker__set = '|'.join((re.escape(x) for x in [
        trans_marker_command_output,
        trans_marker_command_rc,
        trans_marker_decode,
        trans_marker_encode,
        trans_marker_env,
        trans_marker_eval,
    ]))
    trans_marker__ignore = '?'
    trans_marker__begin = "{"
    trans_marker__end = "}"
    trans_marker__escape = "\\"

    value_unset = object()

    def recognize(self, command):
        command = self.strip(command)
        return self.tag_head == '' or \
            command.startswith(self.tag_head) and \
            command[len(self.tag_head):len(self.tag_head) + 1] in ('', ' ')

    def bubble_continue(self, env, marker_node_self, marker_node_target):
        return None

    def exec(self, env, command, marker_node, marker_set):
        pass

    def exit(self):
        raise ExitException()

    def set_var(self, env, array, index, value):
        self.set_var_raw(env, self.get_item(array, index, self.var_name_anonymous), value)

    @staticmethod
    def set_var_raw(env, key, value):
        env.context[key] = value

    def call_func(self, env, func_name, *args, **kwargs):
        args, kwargs = self.var_map_batch(env, *args, **kwargs)
        func = env.context.get(func_name)
        if func is None:
            func = self.eval(env, func_name)
        return func(*args, **kwargs)

    def translate(self, env, s):
        def evaluate(s, default):
            if s.startswith(self.trans_marker__ignore):
                s = s[len(self.trans_marker__ignore):]
                ignore = True
            else:
                ignore = False
            try:
                return self.eval(env, s)
            except NameError:
                if ignore:
                    return default
                else:
                    raise

        def handler(expression, marker, _):
            key = marker[len(self.trans_marker__begin):]
            if key.startswith(self.trans_marker_command_rc):
                return shell_exitcode(expression, env=env.environ())
            elif key.startswith(self.trans_marker_command_output):
                return shell_output(expression, env=env.environ())
            elif key.startswith(self.trans_marker_env):
                return os.getenv(expression)
            elif key.startswith(self.trans_marker_decode):
                value = evaluate(expression, empty_value)
                if value is empty_value:
                    return eval_default_value
                return serializer.load(value)
            elif key.startswith(self.trans_marker_encode):
                value = evaluate(expression, empty_value)
                if value is empty_value:
                    return eval_default_value
                return serializer.dump(value)
            elif key.startswith(self.trans_marker_eval):
                return evaluate(expression, eval_default_value)
            else:
                return evaluate(expression, eval_default_value)

        empty_value = object()
        eval_default_value = ''

        return deep_format(
            s, f"{re.escape(self.trans_marker__begin)}({self.trans_marker__set})?",
            re.escape(self.trans_marker__end), handler, self.trans_marker__escape)

    @classproperty
    @functools.lru_cache(None)
    def final_branch_set(cls):
        return {cls if x is None else x for x in cls.branch_set}

    @staticmethod
    def get_item(array, index, default=None):
        if array:
            try:
                return array[index]
            except IndexError:
                pass
        return default

    @staticmethod
    def strip(command):
        return command.strip()

    @staticmethod
    def split(command, posix=False):
        return shlex.split(command, posix=posix)

    @staticmethod
    def split_raw(command, maxsplit=-1):
        result = []
        for x in command.split(' '):
            x = x.strip()
            if x:
                result.append(x)
        return ' '.join(result).split(' ', maxsplit)

    @staticmethod
    def eval(env, s, v=None):
        return eval(s, env.eval_locals | (v or {}))

    def get_var(self, env, s, v=None):
        try:
            return self.eval(env, s, v)
        except NameError:
            return self.value_unset

    @staticmethod
    def eval_multi(env, s, v=None):
        locals_ = env.eval_locals | (v or {})
        exec(s, locals_)
        return locals_

    @staticmethod
    def var_map(env, s):
        if re.match(r'\$[0-9a-zA-Z_]+$', s):
            return env.eval_locals[s[1:]]
        else:
            return s.replace(r'\$', "$")

    @classmethod
    def var_map_batch(cls, env, *args, **kwargs):
        return [cls.var_map(env, x) for x in args], {k: cls.var_map(env, v) for k, v in kwargs.items()}

    @staticmethod
    def cmd2ak(argv):
        return cmd2ak(argv)


class EndMarker(MarkerBase):
    tag_head = "@end"


class BreakMarker(MarkerBase):
    tag_head = "@break"


class ContinueMarker(MarkerBase):
    tag_head = "@continue"


class MarkerWithEnd(MarkerBase):
    tag_tail = EndMarker


class MarkerShell(MarkerBase):
    shell_cls = None

    def exec(self, env, command, marker_node, marker_set):
        command = self.strip(command)
        if command:
            kwargs = marker_node.payload or {}
            env.shell_cmd(command, self.shell_cls(kwargs), env=env.environ())


class ExitException(Exception):
    pass
