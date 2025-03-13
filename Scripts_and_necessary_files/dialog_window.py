from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit, QApplication, QTextEdit
from PyQt6.QtCore import Qt
from pydomaincontroller import PyDomainController

class DialogWindows(QDialog):
    """A class where user input all the additional info about the operation to be performed on a domain.
    This class is also responsible for a direct communication with PyDomainController by sending enquiries to it
    and also displaying any responses from it."""
    def __init__(self, option:str=""):
        super().__init__()
        self.option = option
        try:
            self.controller = PyDomainController()
        # except LDAPSocketOpenError:
        #     self.controller_response("Nie można połączyć się z serwerem", True)
        except Exception as e:
            error = f"Could not connect to the server \n{str(type(e).__name__)}: {str(e)}"
            self.controller_response((error, True))
        self.initUI()

    def initUI(self):
        """Function that initializes UI of the DialogWindows according to the number of operation sent by the MainWindow"""
        self.layout = QVBoxLayout()
        match self.option:
            case "search":
                self.search()
            case "modify_user":
                self.modify_user()
            case "add_to_group":
                self.add_to_group()
            case "remove_from_group":
                self.remove_from_group()
            case "create_new_ou":
                self.create_new_ou()
            case _:
                pass
        self.setLayout(self.layout)

    def search(self):
        """Function that adjust the dialog window for search operation."""
        self.setWindowTitle("Search")
        s_label = QLabel("Username: ")
        s_line = QLineEdit()
        button = QPushButton("Search")

        self.layout.addWidget(s_label)
        self.layout.addWidget(s_line)
        self.layout.addWidget(button)

        button.clicked.connect(lambda: self.search_formatting(self.controller.search_for(
                                s_line.text(), "User", ["givenName", "sn", "cn", "userPrincipalName", "memberOf"]))
                                if s_line.text() != "" else self.controller_response("Insert username!"))
        # button.clicked.connect(lambda: print(len(
        #     self.controller.search_for(s_line.text(), "Group", ["distinguishedName"], entries=False))))

    def modify_user(self):
        """Function that adjust the dialog window for operation of modifying a user."""
        self.setWindowTitle("Edit user")
        s_label = QLabel("Username: ")
        s_line = QLineEdit()
        nm_label = QLabel("New name: ")
        nm_line = QLineEdit()
        ns_label = QLabel("New surname: ")
        ns_line = QLineEdit()
        ne_label = QLabel("New email: ")
        ne_line = QLineEdit()
        ncn_label = QLabel("New username (the one displayed): ")
        ncn_line = QLineEdit()
        nou_label = QLabel("New OU: ")
        nou_line = QLineEdit()
        button = QPushButton("Modify")

        self.layout.addWidget(s_label)
        self.layout.addWidget(s_line)
        self.layout.addWidget(nm_label)
        self.layout.addWidget(nm_line)
        self.layout.addWidget(ns_label)
        self.layout.addWidget(ns_line)
        self.layout.addWidget(ne_label)
        self.layout.addWidget(ne_line)
        self.layout.addWidget(ncn_label)
        self.layout.addWidget(ncn_line)
        self.layout.addWidget(nou_label)
        self.layout.addWidget(nou_line)
        self.layout.addWidget(button)

        button.clicked.connect(lambda: self.controller_response(self.controller.modify_user(
                                s_line.text(), nm_line.text(), ns_line.text(), ne_line.text(), ncn_line.text(), nou_line.text()))
                                if s_line.text() != "" else self.controller_response("Insert username!"))

    def add_to_group(self):
        """Function that adjust the dialog window for operation of adding user to a group."""
        self.setWindowTitle("Add user to groups")
        s_label = QLabel("Kto: ")
        s_line = QLineEdit()
        g_label = QLabel("Groups:")
        g_line = QTextEdit()
        g_line.setAlignment(Qt.AlignmentFlag.AlignTop)
        g_line.setMaximumSize(300, 75)
        button = QPushButton("Add")

        self.layout.addWidget(s_label)
        self.layout.addWidget(s_line)
        self.layout.addWidget(g_label)
        self.layout.addWidget(g_line)
        self.layout.addWidget(button)

        button.clicked.connect(lambda: self.controller_response(self.controller.change_group(
                                s_line.text(), g_line.toPlainText(), False))
                                if s_line.text() != "" else self.controller_response("Insert username!"))

    def remove_from_group(self):
        """Function that adjust the dialog window for operation of removing user from a group."""
        self.setWindowTitle("Remove user from groups")
        s_label = QLabel("Username: ")
        s_line = QLineEdit()
        g_label = QLabel("Groups:")
        g_line = QTextEdit()
        g_line.setAlignment(Qt.AlignmentFlag.AlignTop)
        g_line.setMaximumSize(300, 75)
        button = QPushButton("Remove")

        self.layout.addWidget(s_label)
        self.layout.addWidget(s_line)
        self.layout.addWidget(g_label)
        self.layout.addWidget(g_line)
        self.layout.addWidget(button)

        button.clicked.connect(lambda: self.controller_response(self.controller.change_group(
                                s_line.text(), g_line.toPlainText(), True))
                                if s_line.text() != "" else self.controller_response("Insert username!"))

    def create_new_ou(self):
        """Function that adjust the dialog window for operation of creating new OU."""
        self.setWindowTitle("Create new OU")
        new_ou_label = QLabel("New OU: ")
        new_ou_line = QLineEdit()
        dest_label = QLabel("Directory of the new OU: ")
        dest_line = QLineEdit()
        button = QPushButton("Create")

        self.layout.addWidget(new_ou_label)
        self.layout.addWidget(new_ou_line)
        self.layout.addWidget(dest_label)
        self.layout.addWidget(dest_line)
        self.layout.addWidget(button)

        button.clicked.connect(lambda: self.controller_response(self.controller.create_new_ou(
                                new_ou_line.text(), dest_line.text()))
                                if new_ou_line.text() != "" and dest_line.text() != "" else
                                (self.controller_response(self.controller.create_new_ou(
                                new_ou_line.text())) if new_ou_line.text() != "" and dest_line.text() == ""
                                else self.controller_response("Insert name of the new OU!")))

    def search_formatting(self, entries):
        """Function that formats the search response from a PyDomainController"""
        formatted_string = ""
        for entry in entries:
                formatted_string += f"{entry}\n\n"
        formatted_string = "No search results found" if formatted_string == "" else formatted_string
        self.controller_response(formatted_string)

    @staticmethod
    def controller_response(response=None):
        """Function responsible for displaying any information coming from PyDomainController
        (no matter if it is a desired response or a content and number of an error)"""
        dialog = QDialog()
        dialog.setWindowTitle("Domain response")
        layout = QVBoxLayout()
        if type(response)==tuple:
            m_text = str(response[0])
            exception = response[1]
        else:
            m_text = str(response)
            exception = False
        response_line = QLabel(m_text)
        button = QPushButton("Ok")
        button.clicked.connect(dialog.done)
        layout.addWidget(response_line)
        layout.addWidget(button)
        dialog.setLayout(layout)
        dialog.exec()
        if exception:
            QApplication.instance().quit()