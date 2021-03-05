from helpers import getClientLanguage

from armagomen.battle_observer.core.bo_constants import GLOBAL

lang = getClientLanguage().lower()


def getLocalization():
    if lang in GLOBAL.RU_LOCALIZATION:
        from armagomen.battle_observer.core.config.hangar.i18n.ru import translate
    elif lang == "de":
        from armagomen.battle_observer.core import translate
    else:
        from armagomen.battle_observer.core import translate
    return translate


localization = getLocalization()
