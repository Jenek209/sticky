from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QApplication, QColorDialog,
                             QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QFont
from PyQt5 import QtSql
import design


class StickyApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        global qApp
        qApp = self
        self.createDB()
        self.windows = []
        self.addSticker(properties={})

    def addSticker(self, properties):
        # Получение последнего id из базы данных
        self.query.exec_("select max(id) from sticky")
        self.query.next()
        # Если он там есть (иначе 0)
        lastid = self.query.value(0) if self.query.value(0) != '' else 0
        properties['id'] = 1 + len(self.windows) + lastid
        self.windows.append(StickyWindow(properties=properties))
        self.windows[-1].show()

    def createDB(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('sticky.db')
        self.db.open()
        self.query = QtSql.QSqlQuery()
        self.query.exec_("create table sticky(id int primary key, "
                    "size varchar(20), font varchar(20), styleSheet text, text text)")

    def save(self, properties):
        insert = "insert into sticky values({id}, '{font}', '{size}', '{styleSheet}', '{text}')".format(**properties)
        self.query.exec_(insert)

    def load(self):
        print('I\'m in self.load()')


class StickyWindow(QMainWindow, design.Ui_Form):
    def __init__(self, properties={}):
        super().__init__()
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
        # Определяются параметры
        self.properties = properties
        # Наследуется размер, шрифт и цвет
        self.setProperties(properties)
        # Сохраняются изменения текста
        self.textEdit.textChanged.connect(self.save)
        # Словарь горячих клавиш
        self.hotkeys = {
            (Qt.Key_S, int(Qt.ControlModifier)): self.save,
            (Qt.Key_L, int(Qt.ControlModifier)): self.load,
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
        menu.addAction('&save', self.save, 'Ctrl+S')
        menu.addAction('&load', self.load, 'Ctrl+L')

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        self.properties['size'] = self.textEdit.property('size')
        qApp.addSticker(self.properties)

    def backgroundColorDialog(self):
        self.bcolor = QColorDialog.getColor()
        if self.bcolor.isValid():
            bcolor = self.bcolor.getRgb()
            self.tcolor.setRgb(*[(x + 122) % 255 for x in bcolor[0:3]], bcolor[3])
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
        newStyleSheet = """
        QTextEdit {{
            background-color:{0};
            color:{1};
        }}
        """.format(self.bcolor.name(), self.tcolor.name())
        self.textEdit.setStyleSheet(newStyleSheet)
        self.properties['styleSheet'] = newStyleSheet

    def fontDialog(self):
        font, ok = QFontDialog.getFont(self.textEdit)
        if ok:
            self.textEdit.setFont(font)
            self.properties['font'] = font.toString()

    def setProperties(self, properties):
        self.resize(properties.get('size', self.textEdit.property('size')))
        font = QFont()
        font.fromString(properties.get('font', self.textEdit.property('font').toString()))
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(properties.get('styleSheet'))
        self.properties['font'] = self.textEdit.property('font').toString()
        self.properties['styleSheet'] = self.textEdit.property('styleSheet')

    def save(self):
        self.properties['size'] = self.textEdit.property('size')
        self.properties['text'] = self.textEdit.toPlainText()
        qApp.save(self.properties)

    def load(self):
        qApp.load()


def main():
    import sys

    app = StickyApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
