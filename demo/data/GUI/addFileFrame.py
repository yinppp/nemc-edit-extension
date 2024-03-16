import os.path

from PyQt6.QtWidgets import QLabel
from qfluentwidgets import MessageBoxBase, LineEdit, SubtitleLabel


class addFileFrame(MessageBoxBase):
    def __init__(self, tip, title, placeholder, path, layout, parent=None):
        super().__init__(parent)
        self.path = path
        self.layout = layout
        self.tipLabel = QLabel(tip)
        self.titleLabel = SubtitleLabel()
        self.titleLabel.setText(title)
        self.lineEdit = LineEdit()
        self.lineEdit.textChanged.connect(self.__textChanged)
        self.lineEdit.setPlaceholderText(placeholder)
        self.viewLayout.addWidget(self.tipLabel)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.lineEdit)
        self.warnLabel = QLabel("* 重复的文件名")
        self.viewLayout.addWidget(self.warnLabel)
        self.widget.setMinimumWidth(350)
        self.warnLabel.hide()
        self.warnLabel.setStyleSheet("color: rgba(255, 0, 0, 255)")
        self.yesButton.setText("创建")
        self.cancelButton.setText("取消")
        self.yesButton.setEnabled(False)

    def __textChanged(self):
        if not os.path.exists(f"{self.path}/{self.lineEdit.text()}.{self.layout}") and self.lineEdit.text():
            self.yesButton.setEnabled(True)
            self.warnLabel.hide()
        else:
            self.yesButton.setEnabled(False)
            if self.lineEdit.text():
                self.warnLabel.show()


def show(window, tip, title, placeholder, path, layout, data):
    w = addFileFrame(tip, title, placeholder, parent=window, path=path, layout=layout)
    if w.exec():
        with open(f"{path}/{w.lineEdit.text()}.{layout}", 'w') as f:
            f.write(data)


