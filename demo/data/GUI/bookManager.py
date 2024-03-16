# coding:utf-8
import datetime
import json
import shutil
import time

import pyperclip
from PyQt6 import QtGui
from qfluentwidgets import (TreeWidget, SimpleCardWidget, TextEdit, CommandBar, Action, InfoBar,
                            InfoBarPosition, MessageBox, Dialog, RoundMenu, CheckBox, MessageBoxBase)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QGridLayout, QTreeWidgetItem, QHeaderView, QButtonGroup
from qfluentwidgets import FluentIcon as FIF
from ..common import config
from ..manager import bookManager
import os
from ..GUI import addFileFrame


class bookMangerInterface(SimpleCardWidget):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.bookTree = TreeWidget()
        self.errBookTree = TreeWidget()
        self.errBookTree.setHeaderLabel("err")
        self.errBookTree.itemClicked.connect(self.__clickErrBookItem)
        self.bookTree.setHeaderLabel("书本")
        self.bookTree.itemClicked.connect(self.__bookTreeItemClicked)
        self.bookTree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookTree.customContextMenuRequested.connect(self.__createTreeMenu)
        self.titleLabel = QLabel()
        self.entryLabel = QLabel()
        self.entryLabel.hide()
        self.fileTextEdit = TextEdit()
        self.fileTextEdit.setEnabled(False)
        self.fileTextEditCommandBar = CommandBar()
        self.isFileTextEditTextChanged = False
        self.fileTextEditCommandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.gridBoxLayout = QGridLayout()
        self.lastTreeItemClicked = None
        if self.__check():
            self.__initBookTree('reset')
        else:
            errorMsg = MessageBox('错误', '请检查路径是否存在或是否存在自定义书本文件', self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()
        self.__initCommon()
        self.__initCommandBar()
        self.__gridBoxLayout()

    def __initCommandBar(self):
        self.fileTextEditCommandBar.addSeparator()
        editAction = Action(FIF.EDIT, '编辑')
        editAction.triggered.connect(self.__editBookFile)
        self.fileTextEditCommandBar.addAction(editAction)
        self.fileTextEditCommandBar.addSeparator()

        self.fileTextEditCommandBar.addSeparator()
        saveAction = Action(FIF.SAVE, '保存', shortcut="Ctrl+S")
        saveAction.triggered.connect(self.__saveFileExitText)
        self.fileTextEditCommandBar.addAction(saveAction)
        self.fileTextEditCommandBar.addSeparator()

        codeAllAction = Action(FIF.CODE, '外部程序打开')
        codeAllAction.triggered.connect(self.__readFileWithOtherWay)
        self.fileTextEditCommandBar.addAction(codeAllAction)
        self.fileTextEditCommandBar.addSeparator()

        backAction = Action(FIF.SAVE_COPY, '备份')
        backAction.triggered.connect(self.__backupBook)
        self.fileTextEditCommandBar.addAction(backAction)
        self.fileTextEditCommandBar.addSeparator()

        updateAction = Action(FIF.UPDATE, '刷新')
        updateAction.triggered.connect(self.__bookTreeUpdateBtnClicked)
        self.fileTextEditCommandBar.addAction(updateAction)
        self.fileTextEditCommandBar.addSeparator()

        copyAllAction = Action(FIF.COPY, '全部复制')
        copyAllAction.triggered.connect(self.__copyAllEditText)
        self.fileTextEditCommandBar.addAction(copyAllAction)
        self.fileTextEditCommandBar.addSeparator()

    def __initCommon(self, projectPath=None):
        if projectPath is None:
            projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
        self.titleLabel.setText(f"当前位置: {projectPath}")

    def __gridBoxLayout(self):
        self.gridBoxLayout.addWidget(self.titleLabel, 0, 0, 1, -1)
        self.gridBoxLayout.addWidget(self.bookTree, 1, 0, 10, 3)
        self.gridBoxLayout.addWidget(self.errBookTree, 11, 0, 10, 3)
        self.gridBoxLayout.addWidget(self.fileTextEdit, 2, 3, 20, 5)
        self.gridBoxLayout.addWidget(self.fileTextEditCommandBar, 1, 3, 1, 4)
        self.gridBoxLayout.addWidget(self.entryLabel, 1, 7, 1, 1)

        self.__widget()

    def __widget(self):
        self.setLayout(self.gridBoxLayout)
        self.show()

    def __initBookTree(self, model=None):
        projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
        if model == 'reset':
            self.lastTreeItemClicked = None
            self.bookTree.clear()
            self.errBookTree.clear()
            self.bookTree.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            projectPath = f"{projectPath}/customBooks"
            try:
                book_manager = bookManager.bookManager(projectPath)
                books, err_list = book_manager.get()
                if err_list:
                    errorMsg = MessageBox('以下文件可能出错',
                                          f'{err_list}',
                                          self.window()
                                          )
                    errorMsg.cancelButton.hide()
                    errorMsg.show()
                    self.__initErrBookTree(err_list)
                for book in books:
                    level1 = QTreeWidgetItem([book['editor_identifier']])
                    self.bookTree.addTopLevelItem(level1)
                    for category in book['category']:
                        level2 = QTreeWidgetItem([f"{category[1]} - {category[0]}"])
                        level1.addChild(level2)
                        thisEntryList = [entry for entry in book['entry'] if entry[2] == category[0].rstrip(".json")]
                        for thisEntry in thisEntryList:
                            book['entry'].remove(thisEntry)
                            level2.addChild(QTreeWidgetItem([f"{thisEntry[1]} - {thisEntry[0]}"]))
                    if book['entry']:
                        errorMsg = MessageBox('无法识别信息',
                                              f'{book["entry"]}',
                                              self.window()
                                              )
                        errorMsg.cancelButton.hide()
                        errorMsg.show()
                        for errFile in book['entry']:
                            self.__initErrBookTree([f"{projectPath}/{book['editor_identifier'].split('-')[0].strip()}/entry/{errFile[0]}"])
                self.__initBackup()

            except Exception as e:
                errorMsg = MessageBox('错误',
                                      f'{e}',
                                      self.window()
                                      )
                errorMsg.cancelButton.hide()
                errorMsg.show()

        elif model == 'clear':
            self.bookTree.clear()
            self.errBookTree.clear()
            self.lastTreeItemClicked = None

    def __editBookFile(self):
        if self.bookTree.currentItem():
            self.fileTextEdit.setEnabled(True)

    def __check(self, projectPath=None):
        if projectPath is None:
            projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
        if projectPath:
            if os.path.exists(f"{projectPath}/customBooks"):
                return True
        return False

    def __isUpdateBookTree(self):
        if self.__check():
            if config.getBoolean(config.IS_UPDATE[0], config.IS_UPDATE[1], config.IS_UPDATE[2]):
                config.setValue(config.IS_UPDATE[0], config.IS_UPDATE[1], config.IS_UPDATE[2], "False")
                return True
        return False

    def updateWidget(self):
        self.__initCommon()
        if self.__isUpdateBookTree():
            self.__initBookTree(model='reset')
            self.fileTextEdit.clear()
        elif not self.__check():
            errorMsg = MessageBox('错误', '请检查路径是否存在或是否存在自定义书本文件', self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()
            self.__initBookTree(model='clear')
            self.fileTextEdit.clear()

    def __saveFileExitText(self):
        if self.fileTextEdit.isEnabled():
            if self.bookTree.selectedItems():
                try:
                    projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1],
                                                  config.PROJECT_PATH[2])
                    editContent = self.fileTextEdit.toPlainText()
                    fileName = self.bookTree.currentItem().text(0).split('-')[1].strip()
                    bookName = self.__getBookName(self.bookTree.currentItem())
                    match self.__getItemType(self.bookTree.currentItem()):
                        case 0:
                            with open(f"{projectPath}/customBooks/{bookName}/{fileName}", 'w', encoding='utf-8') as f:
                                try:
                                    data = json.loads(editContent)
                                except Exception as e:
                                    errorMsg = MessageBox('错误', f"{e}", self.window())
                                    errorMsg.cancelButton.hide()
                                    errorMsg.show()
                                    InfoBar.error(
                                        title='错误',
                                        content="保存失败，json格式错误",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )
                                else:
                                    json.dump(data, f, ensure_ascii=False, indent=4)
                                    self.fileTextEdit.setEnabled(False)
                                    InfoBar.success(
                                        title='Tips',
                                        content="保存成功",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )

                        case 1:
                            with open(f"{projectPath}/customBooks/{bookName}/category/{fileName}", 'w',
                                      encoding='utf-8') as f:
                                try:
                                    data = json.loads(editContent)
                                except Exception as e:
                                    errorMsg = MessageBox('错误', f"{e}", self.window())
                                    errorMsg.cancelButton.hide()
                                    errorMsg.show()
                                    InfoBar.error(
                                        title='错误',
                                        content="保存失败，json格式错误",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )
                                else:
                                    json.dump(data, f, ensure_ascii=False, indent=4)
                                    self.fileTextEdit.setEnabled(False)
                                    InfoBar.success(
                                        title='Tips',
                                        content="保存成功",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )
                        case 2:
                            with open(f"{projectPath}/customBooks/{bookName}/entry/{fileName}", 'w',
                                      encoding='utf-8') as f:
                                try:
                                    data = json.loads(editContent)
                                except Exception as e:
                                    errorMsg = MessageBox('错误', f"{e}", self.window())
                                    errorMsg.cancelButton.hide()
                                    errorMsg.show()
                                    InfoBar.error(
                                        title='错误',
                                        content="保存失败，json格式错误",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )
                                else:
                                    json.dump(data, f, ensure_ascii=False, indent=4)
                                    self.fileTextEdit.setEnabled(False)
                                    InfoBar.success(
                                        title='Tips',
                                        content="保存成功",
                                        isClosable=True,
                                        position=InfoBarPosition.TOP,
                                        duration=1500,
                                        parent=self.window()
                                    )

                except Exception as e:
                    errorMsg = MessageBox('错误', f"{e}", self.window())
                    errorMsg.cancelButton.hide()
                    errorMsg.show()
            else:
                errorMsg = MessageBox('错误', "请先选中文件", self.window())
                errorMsg.cancelButton.hide()
                errorMsg.show()

    def __copyAllEditText(self):
        text = self.fileTextEdit.toPlainText()
        pyperclip.copy(text)
        InfoBar.success(
            title='Tips',
            content="复制成功",
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.window()
        )

    def __readFileWithOtherWay(self):
        try:
            if self.bookTree.selectedItems():
                projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
                fileName = self.bookTree.currentItem().text(0).split('-')[1].strip()
                bookName = self.__getBookName(self.bookTree.currentItem())
                path = ""
                match self.__getItemType(self.bookTree.currentItem()):
                    case 0:
                        path = f"{projectPath}/customBooks/{bookName}/{fileName}"
                    case 1:
                        path = f"{projectPath}/customBooks/{bookName}/category/{fileName}"
                    case 2:
                        path = f"{projectPath}/customBooks/{bookName}/entry/{fileName}"
                if os.path.exists(path):
                    os.startfile(path)
                else:
                    errorMsg = MessageBox('错误', "文件不存在", self.window())
                    errorMsg.cancelButton.hide()
                    errorMsg.show()
            else:
                errorMsg = MessageBox('错误', "请先选中文件", self.window())
                errorMsg.cancelButton.hide()
                errorMsg.show()
        except Exception as e:
            errorMsg = MessageBox('错误', f"{e}", self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()

    def __getItemType(self, treeItem):
        index = 0
        while treeItem.parent():
            index += 1
            treeItem = treeItem.parent()
        return index

    def __getBookName(self, treeItem):
        while treeItem.parent():
            treeItem = treeItem.parent()
        return treeItem.text(0).split('-')[0].strip()

    def __readNewBookTreeItem(self, item):
        try:
            projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
            fileName = item.text(0).split('-')[1].strip()
            bookName = self.__getBookName(item)
            match self.__getItemType(item):
                case 0:
                    if os.path.exists(f"{projectPath}/customBooks/{bookName}/{fileName}"):
                        with open(f"{projectPath}/customBooks/{bookName}/{fileName}", 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.entryLabel.hide()
                            self.fileTextEdit.setText(json.dumps(data, indent=4, ensure_ascii=False))
                    else:
                        errorMsg = MessageBox('错误', "未找到文件", self.window())
                        errorMsg.cancelButton.hide()
                        errorMsg.show()
                        self.__initBookTree()

                case 1:
                    if os.path.exists(f"{projectPath}/customBooks/{bookName}/category/{fileName}"):
                        with open(f"{projectPath}/customBooks/{bookName}/category/{fileName}", 'r',
                                  encoding='utf-8') as f:
                            data = json.load(f)
                            self.entryLabel.hide()
                            self.fileTextEdit.setText(json.dumps(data, indent=4, ensure_ascii=False))
                    else:
                        errorMsg = MessageBox('错误', "未找到文件", self.window())
                        errorMsg.cancelButton.hide()
                        errorMsg.show()
                        self.__initBookTree()

                case 2:
                    if os.path.exists(f"{projectPath}/customBooks/{bookName}/entry/{fileName}"):
                        with open(f"{projectPath}/customBooks/{bookName}/entry/{fileName}", 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            entryList = sorted(os.listdir(f"{projectPath}/customBooks/{bookName}/entry"))
                            index = entryList.index(fileName)
                            self.entryLabel.setText(f"当前章节索引：{index}")
                            self.entryLabel.show()
                            self.fileTextEdit.setText(json.dumps(data, indent=4, ensure_ascii=False))
                    else:
                        errorMsg = MessageBox('错误', "未找到文件", self.window())
                        errorMsg.cancelButton.hide()
                        errorMsg.show()
                        self.__initBookTree()

        except Exception as e:
            errorMsg = MessageBox('错误', f"{e}", self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()

    def __bookTreeItemClicked(self, item, column):
        if not self.fileTextEdit.isEnabled():
            self.__readNewBookTreeItem(item)
            self.lastTreeItemClicked = item
        else:
            w = Dialog("Tips", "您当前正在编辑状态，是否要强制退出", self.window())
            if w.exec():
                self.fileTextEdit.setEnabled(False)
                self.lastTreeItemClicked = item
            else:
                self.bookTree.setCurrentItem(self.lastTreeItemClicked)

    def __bookTreeUpdateBtnClicked(self):
        self.__initBookTree(model='reset')
        self.fileTextEdit.clear()

    def __createTreeMenu(self, pos):
        if self.bookTree.currentItem():
            self.__bookTreeItemClicked(self.bookTree.currentItem(), column=None)
            menu = RoundMenu(parent=self)
            match self.__getItemType(self.bookTree.currentItem()):
                case 0:
                    newFileAction = Action(FIF.ADD, "新建目录")
                    newFileAction.triggered.connect(lambda: self.__addNewBookFile(0, self.bookTree.currentItem()))
                    menu.addAction(newFileAction)
                    menu.move(QtGui.QCursor.pos())
                    menu.show()

                case 1:
                    newFileAction = Action(FIF.ADD, "新建章节")
                    newFileAction.triggered.connect(lambda: self.__addNewBookFile(1, self.bookTree.currentItem()))
                    menu.addAction(newFileAction)
                    menu.move(QtGui.QCursor.pos())
                    menu.show()

    def __addNewBookFile(self, itemType, currentItem):
        if itemType == 0:
            try:
                bookName = self.__getBookName(currentItem)
                projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
                addFileFrame.show(self.window(), f"正在为书本: {bookName}创建目录", "新建目录", "请输入文件名",
                                  f"{projectPath}/customBooks/{bookName}/category", "json", json.dumps({
                        "editor_identifier": bookName,
                    }, indent=4, ensure_ascii=False))
                self.__bookTreeUpdateBtnClicked()
            except Exception as e:
                errorMsg = MessageBox('错误', f'{e}', self.window())
                errorMsg.cancelButton.hide()
                errorMsg.show()

        elif itemType == 1:
            try:
                bookName = self.__getBookName(currentItem)
                categoryName = currentItem.text(0).split('-')[1].strip().rstrip('.json')
                projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1], config.PROJECT_PATH[2])
                addFileFrame.show(self.window(), f"正在为目录: {categoryName}创建章节", "新建章节", "请输入文件名",
                                  f"{projectPath}/customBooks/{bookName}/entry", "json", json.dumps({
                        "editor_identifier": bookName,
                        "pages": [

                        ],
                        "parent": categoryName
                    }, indent=4, ensure_ascii=False
                    ))
                self.__bookTreeUpdateBtnClicked()
            except Exception as e:
                errorMsg = MessageBox('错误', f'{e}', self.window())
                errorMsg.cancelButton.hide()
                errorMsg.show()

    def __initBackup(self):
        bookCount = self.bookTree.topLevelItemCount()
        for i in range(bookCount):
            bookName = self.__getBookName(self.bookTree.topLevelItem(i))
            projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1],
                                          config.PROJECT_PATH[2])
            src = f"{projectPath}/customBooks/{bookName}"
            dst = fr"{os.getcwd()}\backup\book"
            fileList = os.listdir(dst)
            if not os.path.exists(fr"{dst}\{bookName}"):
                hasFile = [fileName for fileName in fileList if fileName.split('-')[0].strip() == bookName]
                if not hasFile:
                    shutil.copytree(src,
                                    fr"{dst}\{bookName} - {time.strftime('%a %b %d %H-%M-%S %Y', time.localtime())}")

    def __backupBook(self):
        try:
            s = MessageBoxBase(self.window())
            s.viewLayout.addWidget(QLabel("请选择要备份的书本:"))
            btnGroup = QButtonGroup(s)
            bookCount = self.bookTree.topLevelItemCount()
            for i in range(bookCount):
                bookName = self.__getBookName(self.bookTree.topLevelItem(i))
                checkBtn = CheckBox(bookName)
                btnGroup.addButton(checkBtn)
                s.viewLayout.addWidget(checkBtn)
            btnGroup.setExclusive(False)
            s.show()
            if s.exec():
                checkBtnList = []
                for btn in btnGroup.buttons():
                    if btn.isChecked():
                        checkBtnList.append(btn.text())
                projectPath = config.getValue(config.PROJECT_PATH[0], config.PROJECT_PATH[1],
                                              config.PROJECT_PATH[2])
                for book in checkBtnList:
                    src = f"{projectPath}/customBooks/{book}"
                    dst = fr"{os.getcwd()}\backup\book"
                    shutil.copytree(src,
                                    fr"{dst}\{book} - {datetime.datetime.now().strftime('%Y-%m-%d  %H-%M-%S')}")
                    InfoBar.success(
                        title='Tips',
                        content=f"书本{book}备份成功",
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=1500,
                        parent=self.window()
                    )

        except Exception as e:
            errorMsg = MessageBox('错误', f'{e}', self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()

    def __initErrBookTree(self, errFiles):
        for errFile in errFiles:
            self.errBookTree.addTopLevelItem(QTreeWidgetItem([errFile]))

    def __clickErrBookItem(self, item):
        filePath = item.text(0)
        try:
            os.startfile(filePath)
        except Exception as e:
            errorMsg = MessageBox('错误', f'{e}', self.window())
            errorMsg.cancelButton.hide()
            errorMsg.show()





