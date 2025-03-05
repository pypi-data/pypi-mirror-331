import re


def cmd2ak(argv):  # arg0 arg1 k0**kwarg0 k1**kwarg1
    args = []
    kwargs = {}
    for x in argv:
        if re.match(r'[0-9a-zA-Z_]+\*\*(?!\*)', x):
            k, v = x.split('**', 1)
            kwargs[k] = v
        else:
            args.append(x.replace(r'\*', "*"))
    return args, kwargs


def ak2cmd(args, kwargs=None):
    result = []
    if args:
        for arg in args:
            result.append(f'"{arg}"')
    if kwargs:
        for k, v in kwargs.items():
            result.append(f'"{k}**{v}"')
    return ' '.join(result)


def pack_context(args, kwargs):
    return {f'__arg{i}': arg for i, arg in enumerate(args, 1)} | {'__args': args, '__kwargs': kwargs} | kwargs
