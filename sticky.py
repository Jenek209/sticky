from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QApplication, QColorDialog,
                             QFontDialog, QDialog,
                             QTableView, QVBoxLayout)
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
        # Получение последнего id из базы данных
        self.query.exec_("select max(id) from sticky")
        self.query.next()
        # Если он там есть (иначе 0)
        self.lastid = self.query.value(0) if self.query.value(0) != '' else 0
        self.ids = []
        self.addSticker(properties={'id': 1 + self.lastid})

    def addSticker(self, properties):
        self.windows.append(StickyWindow(properties=properties.copy()))
        self.windows[-1].show()

    def createDB(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('sticky.db')
        self.db.open()
        self.query = QtSql.QSqlQuery()
        self.query.exec_("create table sticky(id int primary key, "
                    "size varchar(20), font varchar(20), styleSheet text, text text)")

    def save(self, properties):
        insert = "insert or replace into sticky values({id}, '{size}', '{font}', '{styleSheet}', '{text}')".format(**properties)
        self.query.exec_(insert)

    def load(self, sid):
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
    def __init__(self, properties={'id': 0}):
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
        menu.addAction('&load', self.load, 'Ctrl+L')

        menu.exec_(self.mapToGlobal(pos))

    def addSticker(self):
        properties = self.properties.copy()
        properties['id'] = 1 + len(qApp.windows) + qApp.lastid
        properties['size'] = (lambda size: '{0},{1}'.format(size.width(), size.height())) \
            (self.textEdit.property('size'))
        properties['text'] = ''
        qApp.addSticker(properties)

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
        self.styleSheet = """
        QTextEdit {{
            background-color:{0};
            color:{1};
        }}
        """.format(self.bcolor.name(), self.tcolor.name())
        self.textEdit.setStyleSheet(self.styleSheet)
        self.properties['styleSheet'] = self.styleSheet
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
        self.properties['size'] = (lambda size: '{0},{1}'.format(size.width(), size.height()))(self.textEdit.property('size'))
        self.properties['text'] = self.textEdit.toPlainText()
        qApp.save(self.properties)

    def load(self):
        try:
            sid = StickyLoad()
            qApp.load(sid)
        except:
            pass

    def closeEvent(self, event):
        qApp.ids.append(self.properties.get('id'))
        self.save()

    def loadLastClosed(self):
        if len(qApp.ids) > 0:
            qApp.load(qApp.ids.pop(-1))


class StickyLoad(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        # Получение id стикера для загрузки
        self.setLayout(self.myLayout())
        # Словарь горячих клавиш
        self.hotkeys = {
            (Qt.Key_W, int(Qt.ControlModifier)): self.close,
            (Qt.Key_Q, int(Qt.ControlModifier)): qApp.myQuit,
            (Qt.Key_Enter-1, int(Qt.NoModifier)): self.getSID
        }
        self.view.doubleClicked.connect(self.getSID)
        self.exec_()

    def myLayout(self):
        qmodel = QtSql.QSqlQueryModel()
        qmodel.setQuery("select id, text from sticky order by id desc")
        self.view = QTableView(self)
        self.view.setModel(qmodel)
        self.view.verticalHeader().hide()
        self.view.resizeColumnToContents(0)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.selectRow(0)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def getSID(self):
        index = self.view.selectedIndexes()[0]
        self.sid = self.view.model().data(index)
        self.close()

    def keyPressEvent(self, event):
        self.hotkeys.get((event.key(), int(event.modifiers())), lambda: None)()

    def __repr__(self):
        return repr(self.sid)


def main():
    import sys

    app = StickyApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
