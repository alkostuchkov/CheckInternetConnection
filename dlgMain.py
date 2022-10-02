#!/usr/bin/env python3
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

from PyQt5 import QtWidgets, QtCore, QtGui
import dlgMainUI
import dlgAbout
import os
import cCheckInternet


class MainWindow(QtWidgets.QDialog):
    """ Main Class """
    # My SIGNALs
    # when internet connection checked
    internetStatusChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.ui = dlgMainUI.Ui_dlgMain()
        self.ui.setupUi(self)

        # for Translation
        self._dlgMainTranslator = QtCore.QTranslator()
        self._dlgAboutTranslator = QtCore.QTranslator()
        self._qtbasetranslator = QtCore.QTranslator()
        self._translate = QtCore.QCoreApplication.translate

        # FLAGS
        self._isInternet = False

        # checkInternetTimer in the main thread,
        # but checkInternet in the another (QRunnable)
        self._tmrCheckInternet = QtCore.QTimer(self)
        self._tmrCheckInternetInterval = 2000
        self._threadPool = QtCore.QThreadPool()

        # SystemTrayIcon and its context menu
        self._sysTrIcon = QtWidgets.QSystemTrayIcon(self)
        self._trayMenu = QtWidgets.QMenu(self)

        # change cwd to where the program exe is
        # because I DON'T KNOW why the program starts from:
        # C:\Windows\system32 on Windows or /home/username/ on Linux!!!
        self.pathToExe = os.path.abspath(sys.argv[0])
        os.chdir(os.path.dirname(self.pathToExe))

        self._settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)
        #
        # loadSetting must be above createTrayIcon because of __isAppInTray
        # is has been loaded in loadSettings and then checked in createTrayIcon!
        self.readSettings()     # 1
        self.createTrayIcon()   # 2
        self.conConnections()

        # hide to tray on startup
        self.hide()

        # start _tmrCheckInternet
        self._tmrCheckInternet.start(self._tmrCheckInternetInterval)

    def conConnections(self):
        # self.ui.actLangEng.triggered.connect(self.actLangEng_triggered)
        # self.ui.actLangRus.triggered.connect(self.actLangRus_triggered)

        self.ui.actAbout.triggered.connect(self.actAbout_triggered)
        self.ui.actAboutQt.triggered.connect(QtWidgets.qApp.aboutQt)

        self.ui.actQuitApp.triggered.connect(self.actQuitApp_triggered)

        self._sysTrIcon.activated.connect(self.sysTrayIcon_activated)

        # timers
        self._tmrCheckInternet.timeout.connect(self.tmrCheckInternet_timeout)
        self.internetStatusChanged.connect(self.internetStatusChanged_changed)

        self.ui.actStartWithSystem.triggered.connect(self.actStartWithSystem_triggered)
        self.ui.actStartWithSystem.changed.connect(self.actStartWithSystem_changed)

    @QtCore.pyqtSlot()
    def actStartWithSystem_changed(self):
        """ Write settings on actStartWithSystem changed. """
        self.writeSettings()
        self._settings.sync()

    @QtCore.pyqtSlot()
    def actStartWithSystem_triggered(self):
        """ Add or remove app to/from system autorun """
        appName = "CheckInternetConnection"
        if os.name == "nt":  # for Windows
            import winreg
            subKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            value = '"' + self.pathToExe + '"'
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subKey, reserved=0, access=winreg.KEY_ALL_ACCESS)
            except Exception as err:
                QtWidgets.QMessageBox.warning(self,
                self._translate("dlgMain", "Start with system"),
                self._translate("dlgMain", "Cannot add to autorun\n{}").format(err))
            else:
                if self.ui.actStartWithSystem.isChecked():
                    try:
                        winreg.SetValueEx(key, "CheckInternetConnection", 0, winreg.REG_SZ, value)
                    except Exception as err:
                        QtWidgets.QMessageBox.warning(self,
                        self._translate("dlgMain", "Start with system"),
                        self._translate("dlgMain", "Cannot add to autorun\n{}").format(err))
                else:
                    try:
                        winreg.DeleteValue(key, "CheckInternetConnection")
                    except Exception as err:
                        QtWidgets.QMessageBox.warning(self,
                        self._translate("dlgMain", "Start with system"),
                        self._translate("dlgMain", "Cannot delete from autorun\n{}").format(err))
            finally:
                winreg.CloseKey(key)
        elif os.name == "posix":  # for Linux systems
            homeDir = os.environ["HOME"]
            pathToIcon = self.pathToExe + ".ico"
            pathToAutorunDir = "{}/.config/autostart/".format(homeDir)
            pathToAppDir = os.path.dirname(self.pathToExe) + os.path.sep
            pathToAutorunFiledesktop = pathToAutorunDir + "CheckInternetConnection.desktop"
            autorunFileText = "[Desktop Entry]\n" \
                              "Name={}\n" \
                              "Encoding=UTF-8\n" \
                              "Comment=Light weight app for monitoring internet connection\n" \
                              "Path={}\n" \
                              "Exec={}\n" \
                              "Icon={}\n" \
                              "Terminal=false\n" \
                              "Type=Application\n" \
                              "Categories = Network;\n" \
                              "StartupNotify=false\n" \
                              "Hidden=false".format(appName, pathToAppDir, self.pathToExe, pathToIcon)

            if not os.path.exists(pathToAutorunDir):
                QtWidgets.QMessageBox.warning(self,
                self._translate("dlgMain", "Start with system"),
                self._translate("dlgMain", "{} path doesn't exist.\n"
                                         "Cannot add to autorun").format(pathToAutorunDir))
            else:
                if os.path.isfile(pathToAutorunFiledesktop):
                    os.remove(pathToAutorunFiledesktop)
                if self.ui.actStartWithSystem.isChecked():
                    try:
                        myFile = open(pathToAutorunFiledesktop, "w")
                        myFile.write(autorunFileText)
                        # os.system("chmod +x {}".format(autorunFileDesktop))
                    except Exception as err:
                        QtWidgets.QMessageBox.warning(self,
                        self._translate("dlgMain", "Start with system"),
                        self._translate("dlgMain", "Creating autorun file error.\n"
                                                 "Cannot add to autorun").format(err))
                    finally:
                        myFile.close()

    def createTrayIcon(self):
        """ Context trayMenu and SystemTrayIcon """
        self._trayMenu.addAction(self.ui.actStartWithSystem)
        self._trayMenu.addSeparator()
        self._trayMenu.addAction(self.ui.actAbout)
        self._trayMenu.addAction(self.ui.actAboutQt)
        self._trayMenu.addSeparator()
        self._trayMenu.addAction(self.ui.actQuitApp)

        self._sysTrIcon.setContextMenu(self._trayMenu)
        self._sysTrIcon.setIcon(QtGui.QIcon(":/icons/disconnected.png"))
        self._sysTrIcon.setToolTip(self._translate("dlgMain", "Check Internet Connection\nDisconnected"))
        self._sysTrIcon.show()

    def writeSettings(self):
        """ Store program setting to config.ini file """
        # self._settings.beginGroup("LanguageMenu")
        # dActions = dict()
        # for action in self.ui.menu_Options.actions():
        #     if action.isCheckable():
        #         dActions.setdefault(action.text(), action.isChecked())
        # self._settings.setValue("LanguageMenuItems", dActions)
        # self._settings.endGroup()

        self._settings.beginGroup("Check")
        self._settings.setValue("StartWithSystem", self.ui.actStartWithSystem.isChecked())
        self._settings.endGroup()

    def readSettings(self):
        """ Restore program settings from file """
        # self._settings.beginGroup("LanguageMenu")
        # dActions = self._settings.value("LanguageMenuItems")
        # if dActions != None:  # config.ini doesn't exist
        #     for action in self.ui.menu_Options.actions():
        #         if action.isCheckable():
        #             bIsChecked = dActions.get(action.text(), False)
        #             if bIsChecked:  # set checked language
        #                 action.setChecked(bIsChecked)
        #                 if action.text() == "English":
        #                     self.actLangEng_triggered()
        #                 elif action.text() == "Русский":
        #                     self.actLangRus_triggered()
        #                 break
        # self._settings.endGroup()

        self._settings.beginGroup("Check")
        self.ui.actStartWithSystem.setChecked(self._settings.value("StartWithSystem", False, type=bool))
        self._settings.endGroup()

    @QtCore.pyqtSlot()
    def tmrCheckInternet_timeout(self):
        """ Run check internet connection in another thread (QRunnable) """
        checkInternet = cCheckInternet.CCheckInternet()
        checkInternet.signals.result.connect(self.setIsInternet)
        self._threadPool.start(checkInternet)

    @QtCore.pyqtSlot(bool)
    def setIsInternet(self, isInternet):
        """ Set self._isInternet and emit SIGNAL internetStatusChanged """
        # emit internetStatusChanged only if it's realy changed!
        if self._isInternet != isInternet:
            self._isInternet = isInternet
            self.internetStatusChanged.emit()

    @QtCore.pyqtSlot()
    def internetStatusChanged_changed(self):
        """
        Change tray icon depends on self._isInternet.
        """
        if self._isInternet:  # is InternetConnection
            self._sysTrIcon.setIcon(QtGui.QIcon(":/icons/connected.png"))
            self._sysTrIcon.setToolTip(self._translate("dlgMain", "Check Internet Connection\nConnected"))
        else:  # no InternetConnection
            self._sysTrIcon.setIcon(QtGui.QIcon(":/icons/disconnected.png"))
            self._sysTrIcon.setToolTip(self._translate("dlgMain", "Check Internet Connection\nDisconnected"))

    @QtCore.pyqtSlot()
    def actAbout_triggered(self):
        """" About program """
        myDlgAbout = dlgAbout.DlgAbout()
        myDlgAbout.exec_()

    @QtCore.pyqtSlot()
    def actQuitApp_triggered(self):
        """ Quit program completely """
        self.writeSettings()
        self._settings.sync()
        QtWidgets.qApp.quit()

    @QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
    def sysTrayIcon_activated(self, reason):
        """ Mouse events handler """
#todo: process other reasons
        if self._sysTrIcon.isSystemTrayAvailable():
            if reason == 1:
                pass
                # print("Right click") Here is trayIcon context menu
            elif reason == 2:  # Double click
                pass
            # elif reason == QtWidgets.QSystemTrayIcon.Trigger:
            elif reason == 3:  # Left click
                self._trayMenu.popup(QtGui.QCursor.pos())
                # msg = "Connected" if self._isInternet else "Disconnected"
                # self._sysTrIcon.showMessage("Check Internet Connection", msg)
            elif reason == 4:  # Middle click
                self._trayMenu.popup(QtGui.QCursor.pos())
            elif reason == 0:  # Unknown click
                print("Unknown click")
        else:
            print("SystemTray is not available")

    #  def changeEvent(self, e):
        #  """
        #  Retranslate the app when called event LanguageChange.
        #  :param e:
        #  """
        #  if e.type() == QtCore.QEvent.LanguageChange:
            #  self.ui.retranslateUi(self)
            #  # to update translation for systemTrayIcon Message
            #  self._sysTrIcon.setToolTip(self._translate("dlgMain", "Checking. Please wait..."))
        #  else:
            #  QtWidgets.QWidget.changeEvent(self, e)
#
    #  @QtCore.pyqtSlot()
    #  def actLangRus_triggered(self):
        #  """ Translate into Russian """
        #  self.ui.actLangEng.setChecked(False)
        #  self.ui.actLangRus.setChecked(True)
#
        #  self._dlgMainTranslator.load(":/translations/Translations/checkEmail_dlgMain_ru.qm")
        #  self._dlgAboutTranslator.load(":/translations/Translations/checkEmail_dlgAbout_ru.qm")
        #  self._qtbasetranslator.load(":/translations/Translations/qtbase_ru.qm")
#
        #  QtWidgets.QApplication.installTranslator(self._dlgAboutTranslator)
        #  QtWidgets.QApplication.installTranslator(self._dlgMainTranslator)
        #  QtWidgets.QApplication.installTranslator(self._qtbasetranslator)
#
    #  @QtCore.pyqtSlot()
    #  def actLangEng_triggered(self):
        #  """ Translate into English """
        #  self.ui.actLangEng.setChecked(True)
        #  self.ui.actLangRus.setChecked(False)
#
        #  self._dlgAboutTranslator.load(":/translations/Translations/checkEmail_dlgAbout_en.qm")
        #  self._dlgMainTranslator.load(":/translations/Translations/checkEmail_dlgMain_en.qm")
        #  self._qtbasetranslator.load(":/translations/Translations/qtbase_en.qm")
#
        #  QtWidgets.QApplication.installTranslator(self._qtbasetranslator)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # to prevent closing the app when the app is in tray and closed any dialog!!!!!!!!
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    # window.setWindowFlag(QtCore.Qt.Popup, True)
    # window.show()  for showing in tray - don't uncomment!!!!!!!
    sys.exit(app.exec_())
