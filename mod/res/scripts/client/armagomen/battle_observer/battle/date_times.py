from time import strftime

from armagomen.constants import CLOCK
from armagomen.battle_observer.meta.battle.date_times_meta import DateTimesMeta
from armagomen.utils.common import checkDecoder
from armagomen.utils.timers import CyclicTimerEvent


class DateTimes(DateTimesMeta):

    def __init__(self):
        super(DateTimes, self).__init__()
        self.format = None
        self.coding = None
        self.timerEvent = CyclicTimerEvent(CLOCK.UPDATE_INTERVAL, self.updateTimeData)

    def _populate(self):
        super(DateTimes, self)._populate()
        self.format = self.settings[CLOCK.IN_BATTLE][CLOCK.FORMAT]
        self.coding = checkDecoder(strftime(self.format))
        self.as_startUpdateS(self.settings[CLOCK.IN_BATTLE])
        self.timerEvent.start()

    def _dispose(self):
        self.timerEvent.stop()
        super(DateTimes, self)._dispose()

    def updateTimeData(self):
        _time = strftime(self.format)
        if self.coding is not None:
            _time = _time.decode(self.coding)
        self.as_setDateTimeS(_time)
