#!/usr/bin/python3
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

from PyQt5 import QtWidgets, QtCore
import dlgAboutUI
import os
import sys
import webbrowser


class DlgAbout(QtWidgets.QDialog):
    """ Dialog about program, author and thanks """
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = dlgAboutUI.Ui_dlgAbout()
        self.ui.setupUi(self)

        self.installMyEventFilters()
        self.ui.btnClose.clicked.connect(self.btnClose_clicked)

    @QtCore.pyqtSlot()
    def btnClose_clicked(self):
        self.close()

    def showLicence(self):
        """ Show licence in default text editor. """
        pathToLicenceFile = os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep + "COPYING"
        if os.path.exists(pathToLicenceFile):
            webbrowser.open(pathToLicenceFile)

    def installMyEventFilters(self):
        """ Install my event filters. """
        self.ui.lblLicence.installEventFilter(self)
        self.ui.lblLicencePic.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ Event filter. """
        if obj == self.ui.lblLicence or obj == self.ui.lblLicencePic:
            if e.type() == QtCore.QEvent.MouseButtonPress:
                if e.buttons() & QtCore.Qt.LeftButton:
                    self.showLicence()
                    return True
        return QtWidgets.QWidget.eventFilter(self, obj, e)