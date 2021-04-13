from Avatar import PlayerAvatar
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from SoundGroups import SoundModes
from armagomen.battle_observer.core.bo_constants import MAIN, SOUND_MODES, GLOBAL, DAMAGE_LOG
from armagomen.utils.common import setMaxFrameRate, overrideMethod, logInfo, events
from gui.battle_control.arena_visitor import _ClientArenaVisitor
from gui.battle_control.controllers import msgs_ctrl

BASE_NOTIFICATIONS = (msgs_ctrl._ALLY_KILLED_SOUND, msgs_ctrl._ENEMY_KILLED_SOUND)


class BattleCore(object):

    def __init__(self, settings):
        self.settings = settings
        g_playerEvents.onArenaCreated += self.onArenaCreated
        settings.onModSettingsChanged += self.onModSettingsChanged
        overrideMethod(SoundModes, 'setMode')(self.setSoundMode)
        overrideMethod(_ClientArenaVisitor, "hasDogTag")(self.hasDogTag)

    def setSoundMode(self, base, mode, modeName):
        if self.settings.main[MAIN.IGNORE_COMMANDERS]:
            if modeName in SOUND_MODES:
                modeName = SoundModes.DEFAULT_MODE_NAME
        return base(mode, modeName)

    def hasDogTag(self, base, *args, **kwargs):
        return False if self.settings.main[MAIN.HIDE_DOG_TAGS] else base(*args, **kwargs)

    @staticmethod
    def onModSettingsChanged(settings, blockID):
        if blockID == MAIN.NAME:
            if settings[MAIN.ENABLE_FPS_LIMITER]:
                setMaxFrameRate(settings[MAIN.MAX_FRAME_RATE])
            if settings[MAIN.DISABLE_SCORE_SOUND] and msgs_ctrl._ALLY_KILLED_SOUND is not None:
                msgs_ctrl._ALLY_KILLED_SOUND = msgs_ctrl._ENEMY_KILLED_SOUND = None
            elif not settings[MAIN.DISABLE_SCORE_SOUND] and msgs_ctrl._ALLY_KILLED_SOUND is None:
                msgs_ctrl._ALLY_KILLED_SOUND, msgs_ctrl._ENEMY_KILLED_SOUND = BASE_NOTIFICATIONS

    @staticmethod
    @overrideMethod(PlayerAvatar, "getOwnVehicleShotDispersionAngle")
    def getDispersionAngle(base, avatar, *args, **kwargs):
        result = base(avatar, *args, **kwargs)
        events.onDispersionAngleChanged(avatar, result[GLOBAL.FIRST])
        return result

    def onArenaCreated(self):
        if self.settings.log_total[GLOBAL.ENABLED]:
            try:
                dossier = g_currentVehicle.getDossier()
                if dossier:
                    damage = dossier.getRandomStats().getAvgDamage()
                    assist = dossier.getRandomStats().getDamageAssistedEfficiencyWithStan()
                    if damage is not None:
                        damage = round(damage)
                        DAMAGE_LOG.AVG_DAMAGE_DATA = damage
                        logInfo("set vehicle efficiency (avgDamage: {}, avgAssist: {})".format(damage, assist))
            except AttributeError:
                DAMAGE_LOG.AVG_DAMAGE_DATA = GLOBAL.ZERO
