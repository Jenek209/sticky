from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QApplication, QColorDialog,
                             QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
import design


class StickyApp(QMainWindow, design.Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QIcon('Sticky.png'))

        self.setCentralWidget(self.textEdit)
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.myContextMenu)
        self.textEdit.textChanged.connect(self.saveText)

        self.bcolor = QColor('#4c4c4c')
        self.tcolor = QColor('#bdbdbd')

        self.numb = 0


    def keyPressEvent(self, event):
        if ((event.key() == Qt.Key_W) and (event.modifiers() and Qt.ControlModifier)):
            self.close()

        if ((event.key() == Qt.Key_Q) and (event.modifiers() and Qt.ControlModifier)):
            QApplication.instance().quit()

        if ((event.key() == Qt.Key_T) and (event.modifiers() and Qt.ControlModifier)):
            self.addSticker()

        if ((event.key() == Qt.Key_B) and (event.modifiers() and Qt.ControlModifier)):
            self.backgroundColorDialog()

        if ((event.key() == Qt.Key_R) and (event.modifiers() and Qt.ControlModifier)):
            self.textColorDialog()

        if ((event.key() == Qt.Key_O) and (event.modifiers() and Qt.ControlModifier)):
            self.fontDialog()


    def myContextMenu(self, pos):
        menu = QMenu(self)

        menu.addAction('&+', self.addSticker, 'Ctrl+T')
        menu.addAction('&background color', self.backgroundColorDialog, 'Ctrl+B')
        menu.addAction('text colo&r', self.textColorDialog, 'Ctrl+R')
        menu.addAction('text f&ormat', self.fontDialog, 'Ctrl+O')

        menu.exec_(self.mapToGlobal(pos))


    def addSticker(self):
        StickyApp(self).show()


    def backgroundColorDialog(self):
        self.bcolor = QColorDialog.getColor()
        if self.bcolor.isValid():
            self.tcolor.setRgb(*[255-x for x in self.bcolor.getRgb()[0:3]], alpha=self.bcolor.getRgb()[3])
            self.setTextStyleSheet()


    def textColorDialog(self):
        self.tcolor = QColorDialog.getColor()
        if self.tcolor.isValid():
            self.setTextStyleSheet()


    def setTextStyleSheet(self):
        print(self.bcolor.name())
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


    def saveText(self):
        with open('{}.dat'.format(self.numb), 'w') as f:
            f.write(self.textEdit.toPlainText())


def main():
    import sys

    app = QApplication(sys.argv)
    window = StickyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()