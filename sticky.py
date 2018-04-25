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

        self.bcolor = QColor()
        self.tcolor = QColor()


    def myContextMenu(self, pos):

        menu = QMenu(self)

        menu.addAction(QAction(self.tr('+'), self, triggered=self.addSticker))
        menu.addAction('background color', self.backgroundColorDialog)
        menu.addAction('text color', self.textColorDialog)
        menu.addAction('text format', self.fontDialog)

        menu.exec_(self.mapToGlobal(pos))


    def addSticker(self):

        ExampleApp(self).show()


    def backgroundColorDialog(self):

        self.bcolor = QColorDialog.getColor()

        if self.bcolor.isValid():
            self.tcolor = QColor()
            self.tcolor.setRgb(*[255-x for x in self.bcolor.getRgb()[0:3]], alpha=self.bcolor.getRgb()[3])
            self.setTextStyleSheet()


    def textColorDialog(self):

        self.tcolor = QColorDialog.getColor()

        if self.tcolor.isValid():
            self.setTextStyleSheet()


    def setTextStyleSheet(self):

        self.textEdit.setStyleSheet("""
        QTextEdit {{
            background-color:{0};
            color:{1};
        }}
        """.format(self.bcolor.name(), self.tcolor.name()))


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
