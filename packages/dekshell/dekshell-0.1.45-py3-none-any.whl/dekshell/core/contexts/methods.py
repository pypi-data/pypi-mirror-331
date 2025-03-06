import os
import shutil
import tempfile
from itertools import chain
from dektools.module import get_module_attr
from dektools.file import sure_dir, write_file, read_text, remove_path, sure_parent_dir, normal_path, file_desc
from dektools.output import pprint
from dektools.shell import shell_output, shell_exitcode
from dektools.net import get_available_port
from ..encode import encode_run_str
from ..redirect import search_bin_by_path_tree
from ...utils.beep import sound_notify


def _is_true(x):
    if isinstance(x, str):
        x = x.lower()
    return x not in {'false', '0', 'none', 'null', '', ' ', False, 0, None}


def _parent_dir(path, num=1):
    cursor = path
    for i in range(int(num)):
        cursor = os.path.dirname(cursor)
    return cursor


def _list_dir_first(path):
    item = next(iter(os.listdir(path)), '')
    return normal_path(os.path.join(path, item)) if item else item


def _which(x):
    return shutil.which(x) or ''


def _where(x):
    for path in chain(iter([os.getcwd()]), iter(os.environ['PATH'].split(os.pathsep))):
        fp = os.path.join(path, x)
        if os.path.exists(fp):
            return fp
    return ''


default_methods = {
    'venvbin': lambda x, p=None: search_bin_by_path_tree(p or os.getcwd(), x, False),
    'rs': encode_run_str,
    'so': lambda *xx: shell_output(' '.join(xx)),
    'se': lambda *xx: shell_exitcode(' '.join(xx)),
    'print': print,
    'pp': pprint,
    'gma': get_module_attr,
    'chdir': os.chdir,
    'ch': os.chdir,
    'cwd': lambda: os.getcwd(),
    'which': _which,
    'where': _where,
    'lsa': lambda x='.': [normal_path(os.path.join(x, y)) for y in os.listdir(x)],
    'lsf': lambda x='.': _list_dir_first(x),
    'ls': lambda x='.': os.listdir(x),
    'tmpd': lambda: tempfile.mkdtemp(),
    'exist': lambda x: os.path.exists(x),
    'noexist': lambda x: not os.path.exists(x),

    'fd': file_desc,
    'pd': _parent_dir,
    'bn': os.path.basename,
    'sdir': sure_dir,
    'sd': sure_dir,
    'spd': sure_parent_dir,
    'wf': write_file,
    'rt': read_text,
    'rp': remove_path,

    'value': lambda x: x,
    'true': lambda *x: True,
    'false': lambda *x: False,

    'istrue': _is_true,
    'isfalse': lambda x: not _is_true(x),
    'isequal': lambda x, y: x == y,
    'isnotequal': lambda x, y: x != y,
    'beep': lambda x=True: sound_notify(x),

    'net_port': get_available_port,
}
