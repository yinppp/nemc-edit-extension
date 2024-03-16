# coding:utf-8

from PyQt6.QtGui import QFont
from qfluentwidgets import (SettingCardGroup, PushSettingCard,ScrollArea, ExpandLayout, ConfigItem, FolderValidator, MessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QFileDialog
from qfluentwidgets import FluentIcon as FIF

from ..common import config


class SettingInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.projectSettingsGroup = SettingCardGroup(
            "项目文件夹", self.scrollWidget
        )
        self.settingLabel = QLabel(self.tr("设置"), self)
        self.settingLabel.setFont(QFont('黑体', 20))
        self.projectFolderCard = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.FOLDER,
            self.tr("当前目录"),
            parent=self.projectSettingsGroup,
            content=ConfigItem("Folders", "", "", FolderValidator()).value
        )
        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')
        self.scrollWidget.setObjectName('settingScrollWidget')
        self.settingLabel.setObjectName('settingLabel')


        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        self.projectSettingsGroup.addSettingCard(self.projectFolderCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.addWidget(self.projectSettingsGroup)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.__initCard()

    def __initCard(self):
        projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
        if projectPath:
            self.projectFolderCard.setContent(projectPath)
        else:
            self.projectFolderCard.setContent("无")

    def __connectSignalToSlot(self):
        self.projectFolderCard.clicked.connect(self.__choseProjectPath)

    def __choseProjectPath(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("请选择项目文件夹"), "./")
        if folder and config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2]) != folder:
            config.setValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2], folder)
            config.setValue(config.IS_UPDATE[0], config.IS_UPDATE[1], config.IS_UPDATE[2], "True")
            self.projectFolderCard.setContent(folder)
        else:
            if config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2]) == folder:
                errorMsg = MessageBox('提示', '重复的项目文件夹', self.window())
                errorMsg.cancelButton.hide()
                errorMsg.show()

    def updateWidget(self):
        pass
