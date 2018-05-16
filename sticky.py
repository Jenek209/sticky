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
        insert = "insert into sticky values({id}, '{size}', '{font}', '{styleSheet}', '{text}')".format(**properties)
        self.query.exec_(insert)

    def load(self):
        sid = 24
        self.query.exec_("select * from sticky where id = {}".format(sid))
        self.query.next()
        properties = {
            'id': self.query.value(0),
            'size': self.query.value(1),
            'font': self.query.value(2),
            'styleSheet': self.query.value(3),
            'text': self.query.value(4)
        }
        self.addSticker(properties=properties)

    def myQuit(self):
        for window in self.windows:
            window.save()
        self.quit()


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
        self.id = self.properties.get('id')
        # Наследуется размер, шрифт и цвет
        self.setProperties(properties)
        # Сохраняются изменения текста
        self.textEdit.textChanged.connect(self.save)
        # Словарь горячих клавиш
        self.hotkeys = {
            (Qt.Key_S, int(Qt.ControlModifier)): self.save,
            (Qt.Key_L, int(Qt.ControlModifier)): qApp.load,
            (Qt.Key_W, int(Qt.ControlModifier)): self.myClose,
            (Qt.Key_Q, int(Qt.ControlModifier)): qApp.myQuit,
            (Qt.Key_T, int(Qt.ControlModifier)): self.addSticker,
            (Qt.Key_T, int(Qt.ControlModifier) + int(Qt.ShiftModifier)): self.loadLastClosed,
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
        menu.addAction('&load', qApp.load, 'Ctrl+L')

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        self.properties['size'] = (lambda size: '{0},{1}'.format(size.width(), size.height()))(self.textEdit.property('size'))
        qApp.addSticker(self.properties)

    def backgroundColorDialog(self):
        self.bcolor = QColorDialog.getColor()
        if self.bcolor.isValid():
            bcolor = self.bcolor.getRgb()
            self.tcolor.setRgb(*[(x + 122) % 255 for x in bcolor[0:3]], bcolor[3])
            self.setTextStyleSheet()
        else:
            self.bcolor = self.textEdit.palette().color(QPalette.Base)
            self.save()

    def textColorDialog(self):
        self.tcolor = QColorDialog.getColor()
        if self.tcolor.isValid():
            self.setTextStyleSheet()
        else:
            self.tcolor = self.textEdit.palette().color(QPalette.WindowText)
            self.save()

    def setTextStyleSheet(self):
        newStyleSheet = """
        QTextEdit {{
            background-color:{0};
            color:{1};
        }}
        """.format(self.bcolor.name(), self.tcolor.name())
        self.textEdit.setStyleSheet(newStyleSheet)
        self.properties['styleSheet'] = newStyleSheet
        self.save()

    def fontDialog(self):
        font, ok = QFontDialog.getFont(self.textEdit)
        if ok:
            self.textEdit.setFont(font)
            self.properties['font'] = font.toString()
            self.save()

    def setProperties(self, properties):
        size = properties.get('size', (lambda size: '{0},{1}'.format(size.width(), size.height()))(self.textEdit.property('size')))
        self.resize(*[int(value) for value in size.split(',')])
        fontString = properties.get('font', '')
        fontString = self.textEdit.property('font').toString() if fontString == '' else fontString
        font = QFont()
        font.fromString(fontString)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(properties.get('styleSheet'))
        self.textEdit.setText(properties.get('text', ''))
        self.properties['font'] = self.textEdit.property('font').toString()
        self.properties['styleSheet'] = self.textEdit.property('styleSheet')

    def save(self):
        self.properties['id'] = self.id
        self.properties['size'] = (lambda size: '{0},{1}'.format(size.width(), size.height()))(self.textEdit.property('size'))
        self.properties['text'] = self.textEdit.toPlainText()
        qApp.save(self.properties)

    def myClose(self):
        self.save()
        self.close()

    def loadLastClosed(self):
        print('I\'m in StickyWindow.loadLastClosed()')


def main():
    import sys

    app = StickyApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
