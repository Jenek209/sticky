import sys
from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication, QAction, QColorDialog, QFontDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QColor

import design

class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.setCentralWidget(self.textEdit)

        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.myContextMenu)

    def myContextMenu(self, pos):

        menu = QMenu(self)

        menu.addAction(QAction(self.tr('+'), self, triggered=self.addSticker))
        menu.addAction('color', self.colorDialog)
        menu.addAction('format', self.fontDialog)

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        ExampleApp(self).show()

    def colorDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.textEdit.setStyleSheet("QTextEdit {background-color:%s}}" % color.name())

    def fontDialog(self):
        font, ok = QFontDialog.getFont()

        if ok:
            self.textEdit.setFont(font)


def main():
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
