from dialog_window import DialogWindows
import sys
from PyQt6.QtWidgets import QWidget, QApplication, QGraphicsView, QPushButton, QVBoxLayout
from PyQt6.QtCore import QSize

class MainWindow(QWidget):
    """Class that displays the window with all the implemented operations that can be performed on a domain."""
    def __init__(self):
        super().__init__()
        self.max_size = QSize(400, 50)
        self.resize(400, 300)
        self.view = QGraphicsView()
        self.initUI()
        self.setWindowTitle("Main menu")

    def initUI(self):
        """Function that initializes UI of the MainWindow class (buttons etc.)."""
        self.layout = QVBoxLayout()

        self.search_button = QPushButton("Search")
        self.search_button.setMaximumSize(self.max_size)
        self.search_button.clicked.connect(lambda: self.open_dialog("search"))
        self.layout.addWidget(self.search_button)

        self.modify_button = QPushButton("Modify user")
        self.modify_button.setMaximumSize(self.max_size)
        self.modify_button.clicked.connect(lambda: self.open_dialog("modify_user"))
        self.layout.addWidget(self.modify_button)

        self.add_to_group = QPushButton("Add user to groups")
        self.add_to_group.setMaximumSize(self.max_size)
        self.add_to_group.clicked.connect(lambda: self.open_dialog("add_to_group"))
        self.layout.addWidget(self.add_to_group)

        self.remove_from_group = QPushButton("Remove user from groups")
        self.remove_from_group.setMaximumSize(self.max_size)
        self.remove_from_group.clicked.connect(lambda: self.open_dialog("remove_from_group"))
        self.layout.addWidget(self.remove_from_group)

        self.add_ou = QPushButton("Create new OU")
        self.add_ou.setMaximumSize(self.max_size)
        self.add_ou.clicked.connect(lambda: self.open_dialog("create_new_ou"))
        self.layout.addWidget(self.add_ou)

        self.setLayout(self.layout)

    def open_dialog(self, option=""):
        """Function that opens a dialog window where user should input all the additional info about the operation to be performed."""
        self.dialog_window = DialogWindows(option=option)
        self.dialog_window.exec()

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()