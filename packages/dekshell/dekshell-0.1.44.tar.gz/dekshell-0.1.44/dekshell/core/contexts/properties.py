import os
import sys
import shutil
from sysconfig import get_paths
from importlib import metadata
from dektools.module import ModuleProxy
from ..redirect import shell_name
from ...utils.serializer import serializer

current_shell = shutil.which(shell_name, path=get_paths()['scripts'])


def make_shell_properties(shell):
    return {
        'shell': shell,
        'shr': f'{shell} r',
        'shrf': f'{shell} rf',
        'shrfc': f'{shell} rfc',
        'shrs': f'{shell} rs',
        'shrrs': f'{shell} rrs',
    }


package_name = __name__.partition(".")[0]
path_home = os.path.expanduser('~')
is_on_win = os.name == "nt"
path_root = path_home[:path_home.find(os.sep)] if is_on_win else os.sep

default_properties = {
    '__meta__': {
        'name': package_name,
        'version': metadata.version(package_name)
    },
    'python': sys.executable,
    **make_shell_properties(current_shell),
    'pid': os.getpid(),
    'pname': os.path.basename(sys.executable),
    'root': path_root,
    'home': path_home,

    'oswin': is_on_win,
    'ops': os.pathsep,
    'oss': os.sep,

    'ser': serializer,

    'mp': ModuleProxy(),
}
