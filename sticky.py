from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QApplication, QColorDialog,
                             QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette
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
        # Добавление иконки
        self.setWindowIcon(QIcon('Sticky.png'))
        # Заполнение окна текстовым редактором и обработка контекстного меню
        self.setCentralWidget(self.textEdit)
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.myContextMenu)
        # Системный цвет фона и текста
        self.bcolor = self.textEdit.palette().color(QPalette.Base)
        self.tcolor = self.textEdit.palette().color(QPalette.WindowText)
        # Наследуется размер, шрифт и цвет
        if properties is not None:
            self.setProperties(properties)

        self.hotkeys = {
            (Qt.Key_W, int(Qt.ControlModifier)): self.close,
            (Qt.Key_Q, int(Qt.ControlModifier)): QApplication.instance().quit,
            (Qt.Key_T, int(Qt.ControlModifier)): self.addSticker,
            (Qt.Key_T, int(Qt.ControlModifier) + int(Qt.ShiftModifier)): self.load,
            (Qt.Key_B, int(Qt.ControlModifier)): self.backgroundColorDialog,
            (Qt.Key_R, int(Qt.ControlModifier)): self.textColorDialog,
            (Qt.Key_O, int(Qt.ControlModifier)): self.fontDialog
        }

    def keyPressEvent(self, event):
        self.hotkeys.get((event.key(), int(event.modifiers())), lambda: None)()

    def myContextMenu(self, pos):
        menu = QMenu(self)

        menu.addAction('&+', self.addSticker, 'Ctrl+T')
        menu.addAction('&background color', self.backgroundColorDialog, 'Ctrl+B')
        menu.addAction('text colo&r', self.textColorDialog, 'Ctrl+R')
        menu.addAction('text f&ormat', self.fontDialog, 'Ctrl+O')

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        properties = {
            'size': self.textEdit.property('size'),
            'font': self.textEdit.property('font'),
            'styleSheet': self.textEdit.property('styleSheet')
        }
        qApp.addSticker(properties)

    def backgroundColorDialog(self):
        self.bcolor = QColorDialog.getColor()
        if self.bcolor.isValid():
            bcolor = self.bcolor.getRgb()
            self.tcolor.setRgb(*[255 - x for x in bcolor[0:3]], bcolor[3])
            self.setTextStyleSheet()
        else:
            self.bcolor = self.textEdit.palette().color(QPalette.Base)

    def textColorDialog(self):
        self.tcolor = QColorDialog.getColor()
        if self.tcolor.isValid():
            self.setTextStyleSheet()
        else:
            self.tcolor = self.textEdit.palette().color(QPalette.WindowText)

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

    def load(self):
        print('I\'m in self.load()')


def main():
    import sys

    app = Sticky(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
