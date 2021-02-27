from math import degrees

from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.battle_control import matrix_factory
from gui.battle_control.battle_constants import VEHICLE_LOCATION
from ..core.bo_constants import GLOBAL, MINIMAP
from ..core import cfg, b_core
from ..core.utils import overrideMethod


class BOPersonalEntriesPlugin(plugins.PersonalEntriesPlugin):

    def __init__(self, *args, **kwargs):
        super(BOPersonalEntriesPlugin, self).__init__(*args, **kwargs)

    def start(self):
        super(BOPersonalEntriesPlugin, self).start()
        if self._PersonalEntriesPlugin__yawLimits is None:
            vInfo = self._arenaDP.getVehicleInfo()
            yawLimits = vInfo.vehicleType.turretYawLimits
            if yawLimits is not None:
                self._PersonalEntriesPlugin__yawLimits = (degrees(yawLimits[0]), degrees(yawLimits[1]))


class VehiclesPlugin(plugins.ArenaVehiclesPlugin):

    def __init__(self, *args, **kwargs):
        super(VehiclesPlugin, self).__init__(*args, **kwargs)

    def _showVehicle(self, vehicleID, location):
        entry = self._entries.get(vehicleID, None)
        if entry is not None and entry.isAlive():
            matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, location, self._arenaVisitor.getArenaPositions())
            if matrix is not None:
                self._ArenaVehiclesPlugin__setLocationAndMatrix(entry, location, matrix)
                self._setInAoI(entry, True)
                self._ArenaVehiclesPlugin__setActive(entry, True)

    def _hideVehicle(self, entry):
        if entry.isAlive() and entry.isActive():
            matrix = entry.getMatrix()
            if matrix is not None:
                matrix = matrix_factory.convertToLastSpottedVehicleMP(matrix)
            self._setInAoI(entry, False)
            self._ArenaVehiclesPlugin__setLocationAndMatrix(entry, VEHICLE_LOCATION.UNDEFINED, matrix)

    def _ArenaVehiclesPlugin__setDestroyed(self, vehicleID, entry):
        self._ArenaVehiclesPlugin__clearAoIToFarCallback(vehicleID)
        if not entry.wasSpotted() and entry.setAlive(False) and entry.getMatrix() is not None:
            if not entry.isActive():
                self._ArenaVehiclesPlugin__setActive(entry, True)
            if entry.isActive() and not entry.isInAoI():
                self._setInAoI(entry, True)
            self._invoke(entry._entryID, 'setDead', True)
            self._move(entry._entryID, CONTAINER_NAME.DEAD_VEHICLES)
            self._invoke(entry._entryID, self._showNames)
        else:
            self._ArenaVehiclesPlugin__setActive(entry, False)

    @property
    def _showNames(self):
        if cfg.minimap[MINIMAP.DEATH_PERMANENT] and cfg.minimap[MINIMAP.SHOW_NAMES]:
            return 'showVehicleName'
        return 'hideVehicleName'


@overrideMethod(MinimapComponent, "_setupPlugins")
def _setupPlugins(base, plugin, arenaVisitor):
    if cfg.minimap[GLOBAL.ENABLED] and b_core.isAllowedBattleType(arenaVisitor)[0]:
        setup = {'equipments': plugins.EquipmentsPlugin,
                 'vehicles': VehiclesPlugin if cfg.minimap[MINIMAP.DEATH_PERMANENT] else plugins.ArenaVehiclesPlugin,
                 'personal': BOPersonalEntriesPlugin,
                 'area': plugins.AreaStaticMarkerPlugin}
        return setup
    else:
        return base(plugin, arenaVisitor)
