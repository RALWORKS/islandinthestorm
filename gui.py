"""
Island in the Storm GUI
Based on IFP Qt GUI by JSMaika (https://github.com/JSMaika/IFP-Qt-GUI)

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>


To use this GUI, create a QApplication in your game file, and
create an instance of the App class defined here, then
pass it into your IFPGame instance

    from PyQt5.QtWidgets import QApplication
    from ifp_qt_gui.gui import Player
    from intficpy.ifp_game import IFPGame

    me = Player("yourself")

    q_application = QApplication(sys.argv)
    app = App()
    game = IFPGame(me, app)

After the content of your game, show the Qt GUI

    game.initGame()
    app.show()
    sys.exit(q_application.exec_())

"""

import os

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QPushButton,
    QAction,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QAbstractSlider,
    QSizePolicy,
    QFileDialog,
)
from PyQt5.QtGui import QIcon, QFont, QIcon


class App(QMainWindow):
    """
    The UI App class
    Pass an instance into your IFPGame object
    """

    app_style = """
        #MainWindow {
            background-image: url(island_bg2.png);
            background-color: #000000;
        }
        QLineEdit {
            background: #ffffff;
            font-size: 18px;
        }
    """

    container_style = """
        QWidget {
            background-color: transparent;
            background-image: none;
            border: none;
        }
        QScrollBar:vertical {
            border: none;
            background: #a3a3a3;
            border-radius: 6px;
            width: 30px;
            margin: 10px 8px 10px 8px;
        }

        QScrollBar::handle:vertical {
            background: #ffffff;
            border-radius: 6px;
            min-height: 15px;
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: top left;
            subcontrol-origin: margin;
            position: absolute;
        }

        QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """

    def __init__(self):
        """
        Initialize the GUI
        """
        super().__init__()

        # self.icon = None
        # self.setWindowIcon(QIcon(self.icon))

        self.setObjectName("MainWindow")

        self.title = "Island in the Storm"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

        self.initUI()
        self.showMaximized()
        self.game = None

    def initUI(self):
        """
        Build the basic user interface
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet(self.app_style)

        # self.widget.resize(self.width, self.height)
        # self.widget.setLayout(self.main_layout)

        #   Container Widget
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.main_layout = QVBoxLayout()
        self.widget.setLayout(self.main_layout)

        # TextBox
        self.textbox = QLineEdit()
        self.textbox.resize(280, 30)

        #   Scroll Area Properties
        self.scroll_container = QWidget()
        self.scroll_container.setStyleSheet(self.container_style)
        self.scroll_container_layout = QVBoxLayout(self.scroll_container)

        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout()
        self.scroll_widget_layout.setContentsMargins(15, 15, 15, 30)
        self.scroll_widget.setLayout(self.scroll_widget_layout)

        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.Box)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_container_layout.addWidget(self.scroll)

        self.scroll_widget_layout.setAlignment(QtCore.Qt.AlignTop)

        self.main_layout.addWidget(self.scroll_container)
        self.main_layout.addWidget(self.textbox)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.cutscene = []
        self.anykeyformore = False

    def send_turn_input(self):
        """
        Send player input to the game, and clear the input field
        """
        textboxValue = self.textbox.text()
        self.textbox.setText("")
        self.game.turnMain(textboxValue)

    def keyPressEvent(self, event):
        """
        Handle key press events
        
        Enter - send turn input
        Up - move backward through command history
        Down - move forward through command history
        """
        if event.key() == QtCore.Qt.Key_Up:
            self.textbox.setText(self.game.getCommandUp())

        elif event.key() == QtCore.Qt.Key_Down:
            self.textbox.setText(self.game.getCommandDown())

        elif event.key() == QtCore.Qt.Key_Return and len(self.textbox.text()) > 0:
            self.send_turn_input()

    def printEventText(self, event):
        """
        Prints game output to the GUI, and scrolls down
        Takes a single argument event, the event to print
        """
        self.obox = QFrame()
        self.obox.setFrameStyle(QFrame.StyledPanel)
        self.obox.setStyleSheet(event.style)

        self.scroll_widget_layout.addWidget(self.obox)
        self.olayout = QVBoxLayout()
        self.obox.setLayout(self.olayout)

        for t in event.text:
            out = QLabel()
            out.setText(t)
            self.olayout.addWidget(out)
            out.setWordWrap(True)
            out.setStyleSheet("margin-bottom: 5px")
            out.setMaximumSize(out.sizeHint())
            out.setMinimumSize(out.sizeHint())

        self.obox.setMaximumSize(self.obox.sizeHint())
        self.obox.setMinimumSize(self.obox.sizeHint())
        vbar = self.scroll.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))

    def saveFilePrompt(self, extension, filetype_desc, msg):
        """
        Create a prompt to save a file
        Used for saving the game, and creating recordings
        """
        cwd = os.getcwd()
        fname = QFileDialog.getSaveFileName(
            self, msg, cwd, f"{filetype_desc} (*{extension})"
        )
        fname = fname[0]
        if len(fname) == 0:
            return None

        if fname.endswith(extension):
            return fname

        if "." in fname:
            fname = fname[: fname.index(".")]

        return fname + extension

    def openFilePrompt(self, extension, filetype_desc, msg):
        """
        Create a prompt to open a file
        Used for loading save files and playing back recordings
        """
        cwd = os.getcwd()
        fname = QFileDialog.getOpenFileName(
            self, msg, cwd, f"{filetype_desc} (*{extension})"
        )
        if not fname[0].endswith(extension):
            return None

        return fname[0]
