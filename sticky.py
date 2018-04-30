from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QApplication, QColorDialog,
                             QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
import design


class Sticky(QApplication):
    def __init__(self, args):
        super().__init__(args)
        global qApp
        qApp = self
        self.windows = []
        self.addSticker(properties=None)

    def addSticker(self, properties):
        self.windows.append(StickyWindow(properties=properties))
        self.windows[-1].show()


class StickyWindow(QMainWindow, design.Ui_Form):
    def __init__(self, parent=None, properties=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QIcon('Sticky.png'))

        self.setCentralWidget(self.textEdit)
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.myContextMenu)

        self.bcolor = QColor('#4c4c4c')
        self.tcolor = QColor('#bdbdbd')

        self.numb = 0

        if properties is not None:
            self.setProperties(properties)

        self.hotkeys = {
            Qt.Key_W: (Qt.ControlModifier, lambda self: self.close()),
            Qt.Key_Q: (Qt.ControlModifier, lambda self: QApplication.instance().quit()),
            Qt.Key_T: (Qt.ControlModifier, lambda self: self.addSticker()),
            Qt.Key_B: (Qt.ControlModifier, lambda self: self.backgroundColorDialog()),
            Qt.Key_R: (Qt.ControlModifier, lambda self: self.textColorDialog()),
            Qt.Key_O: (Qt.ControlModifier, lambda self: self.fontDialog()),
        }

    def keyPressEvent(self, event):
        modifiers, handler = self.hotkeys.get(event.key(), (False, False))
        if event.modifiers() and modifiers:
            handler(self)

    def myContextMenu(self, pos):
        menu = QMenu(self)

        menu.addAction('&+', self.addSticker, 'Ctrl+T')
        menu.addAction('&background color', self.backgroundColorDialog, 'Ctrl+B')
        menu.addAction('text colo&r', self.textColorDialog, 'Ctrl+R')
        menu.addAction('text f&ormat', self.fontDialog, 'Ctrl+O')

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        properties = {
            'size' : self.textEdit.property('size'),
            'font' : self.textEdit.property('font'),
            'styleSheet' : self.textEdit.property('styleSheet')
        }
        qApp.addSticker(properties)

    def backgroundColorDialog(self):
        self.bcolor = QColorDialog.getColor()
        if self.bcolor.isValid():
            bcolor = self.bcolor.getRgb()
            self.tcolor.setRgb(*[255 - x for x in bcolor[0:3]], bcolor[3])
            self.setTextStyleSheet()
        else:
            self.bcolor = QColor('#4c4c4c')

    def textColorDialog(self):
        self.tcolor = QColorDialog.getColor()
        if self.tcolor.isValid():
            self.setTextStyleSheet()
        else:
            self.tcolor = QColor('#bdbdbd')

    def setTextStyleSheet(self):
        self.textEdit.setStyleSheet("""
        QTextEdit {{
            background-color:{0};
            color:{1};
        }}
        """.format(self.bcolor.name(), self.tcolor.name()))

    def fontDialog(self):
        font, ok = QFontDialog.getFont(self.textEdit)
        if ok:
            self.textEdit.setFont(font)

    def setProperties(self, properties):
        self.resize(properties['size'])
        self.textEdit.setFont(properties['font'])
        self.textEdit.setStyleSheet(properties['styleSheet'])


def main():
    import sys

    app = Sticky(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
