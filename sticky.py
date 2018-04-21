import sys
from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication
from PyQt5.QtCore import Qt
import design

class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setCentralWidget(self.textEdit)
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.my_context_menu)

    def my_context_menu(self, pos):

        menu = QMenu(self)

        firstAct = menu.addAction("firstAct")
        secondAct = menu.addAction("secondAct")

        action = menu.exec_(self.sender().mapToGlobal(pos))

        menu.exec_(self.mapToGlobal(pos))

def main():
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
