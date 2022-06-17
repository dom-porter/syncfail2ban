from AliasController import AliasController


class Firewall(object):

    def __init__(self, device):
        self._device = device

    @property
    def alias_controller(self) -> AliasController:
        return AliasController(self._device)
