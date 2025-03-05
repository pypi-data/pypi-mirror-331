from .base import MarkerBase, MarkerWithEnd


class FunctionMarker(MarkerWithEnd):
    tag_head = "@func"

    def exec(self, env, command, marker_node, marker_set):
        self.set_var_raw(env, command, marker_node.children[:])


class CallMarker(MarkerBase):
    tag_head = "@call"

    def exec(self, env, command, marker_node, marker_set):
        raise NotImplementedError


class GlobalMarker(MarkerBase):
    tag_head = "@global"

    def exec(self, env, command, marker_node, marker_set):
        raise NotImplementedError


class NonlocalMarker(MarkerBase):
    tag_head = "@nonlocal"

    def exec(self, env, command, marker_node, marker_set):
        raise NotImplementedError
