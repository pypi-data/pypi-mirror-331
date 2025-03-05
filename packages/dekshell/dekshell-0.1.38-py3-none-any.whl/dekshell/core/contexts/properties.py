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
try:
    package_version = metadata.version(metadata.version(package_name))
except:
    package_version = None

default_properties = {
    '__meta__': {
        'name': package_name,
        'version': package_version
    },
    'python': sys.executable,
    **make_shell_properties(current_shell),
    'pid': os.getpid(),
    'pname': os.path.basename(sys.executable),

    'os_name': os.name,
    'platform': sys.platform,
    'os_win': os.name == "nt",
    'home': os.path.expanduser('~'),

    'ser': serializer,

    'mp': ModuleProxy(),
}
