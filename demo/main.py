# coding:utf-8
import os
import sys

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import QApplication, QStackedWidget, QHBoxLayout

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme, NavigationAvatarWidget)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from data.GUI import settings, bookManager


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        self.bookManagerInterface = bookManager.bookMangerInterface(self)
        self.settingsInterface = settings.SettingInterface(self)

        self.initLayout()

        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.bookManagerInterface, FIF.BOOK_SHELF, '书本管理')

        self.navigationInterface.addSeparator()

        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('yin', fr"{os.getcwd()}\_internal\resource\yin.png" if getattr(sys, "frozen", False)  else fr'{os.getcwd()}\resource\yin.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(self.settingsInterface, FIF.SETTING, '设置', None,
                             NavigationItemPosition.BOTTOM)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('Edit Extension')
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.setMinimumWidth(w // 2 + self.width() // 2)
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.setQss()

    def addSubInterface(self, interface, icon, text: str, on_click=None, position=NavigationItemPosition.TOP,
                        parent=None):
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=(lambda: self.switchTo(interface)) if on_click is None else (lambda: on_click(interface)),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        if getattr(sys, "frozen", False):
            path = fr"{os.getcwd()}\_internal\resource\{color}\demo.qss"
        else:
            path = fr'{os.getcwd()}\resource\{color}\demo.qss'
        with open(path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        widget.updateWidget()
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '开源地址',
            'https://github.com/yinppp/nemc-edit-extension/',
            self
        )
        w.yesButton.setText('访问网站')
        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/yinppp/nemc-edit-extension/"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Window()
    mainWindow.show()
    app.exec()



