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


    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_W) and (event.modifiers() and Qt.ControlModifier):
            self.close()

        if (event.key() == Qt.Key_Q) and (event.modifiers() and Qt.ControlModifier):
            QApplication.instance().quit()

        if (event.key() == Qt.Key_T) and (event.modifiers() == Qt.ControlModifier):
            self.addSticker()

        if (event.key() == Qt.Key_B) and (event.modifiers() and Qt.ControlModifier):
            self.backgroundColorDialog()

        if (event.key() == Qt.Key_R) and (event.modifiers() and Qt.ControlModifier):
            self.textColorDialog()

        if (event.key() == Qt.Key_O) and (event.modifiers() and Qt.ControlModifier):
            self.fontDialog()

        #if (event.key() == Qt.Key_T) and (event.modifiers() and Qt.ControlModifier) \
        #        and (event.modifiers() and Qt.ShiftModifier):
        #    self.loadText()

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
