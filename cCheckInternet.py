# -*- coding: utf-8 -*-

"""
This file is part of CheckInternetConnection.

    CheckInternetConnection is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CheckInternetConnection is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CheckInternetConnection.  If not, see <https://www.gnu.org/licenses/>.

  (Этот файл — часть CheckInternetConnection.

   CheckInternetConnection - свободная программа: вы можете перераспространять ее и/или
   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
   в каком она была опубликована Фондом свободного программного обеспечения;
   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
   версии.

   CheckInternetConnection распространяется в надежде, что она будет полезной,
   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
   общественной лицензии GNU.

   Вы должны были получить копию Стандартной общественной лицензии GNU
   вместе с этой программой. Если это не так, см.
   <https://www.gnu.org/licenses/>.)
"""

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
import urllib.request


class CCheckInternetSignals(QObject):
    """ Signals for CCheckInternet class """
    result = pyqtSignal(bool)


class CCheckInternet(QRunnable):
    """ Thread is run by self._tmrCheckInternet in dlgMain.py """

    def __init__(self):
        QRunnable.__init__(self)
        self.signals = CCheckInternetSignals()

    def run(self):
        try:
            urllib.request.urlopen("https://www.google.com")
            self.signals.result.emit(True)
        except:
            try:  # if www.google.com is not available try www.yandex.ru
                urllib.request.urlopen("https://www.yandex.ru")
                self.signals.result.emit(True)
            except:
                self.signals.result.emit(False)
        finally:
            pass
            # print("DoCheckInternetConnection (QRunnable) finished...")