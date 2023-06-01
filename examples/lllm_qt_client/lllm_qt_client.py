import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit,QHBoxLayout, QLineEdit, QVBoxLayout, QWidget, QToolBar, QAction, QPushButton, QStatusBar, QComboBox
from PyQt5.QtSvg import QSvgWidget
from socketio.client import Client
from socketio.exceptions import ConnectionError
from pathlib import Path

class ServerConnector(QObject):
    text_chunk_received = pyqtSignal(str)
    text_generated = pyqtSignal(str)
    connection_failed = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)
    personalities_received = pyqtSignal(list)

    def __init__(self, parent=None):
        super(ServerConnector, self).__init__(parent)
        self.socketio = Client()
        self.connected = False
        self.personalities = []
        self.selected_personality = "default_personality"

        self.socketio.on('connect', self.handle_connect)
        self.socketio.on('text_chunk', self.handle_text_chunk)
        self.socketio.on('text_generated', self.handle_text_generated)
        self.socketio.on('personalities_list', self.handle_personalities_received)

    def handle_connect(self):
        self.socketio.emit('connect')

    def connect_to_server(self):
        if not self.connected:
            try:
                self.socketio.connect('http://localhost:9600')
                self.connected = True
                self.connection_status_changed.emit(True)
                self.list_personalities()
            except ConnectionError:
                self.connection_failed.emit()
                self.connection_status_changed.emit(False)

    def disconnect_from_server(self):
        if self.connected:
            self.socketio.disconnect()
            self.connected = False
            self.connection_status_changed.emit(False)

    def list_personalities(self):
        self.socketio.emit('list_personalities')

    @pyqtSlot(str)
    def generate_text(self, prompt):
        if not self.connected:
            self.connection_failed.emit()
            return

        data = {
            'client_id': self.socketio.sid,
            'prompt': prompt,
            'personality': self.selected_personality
        }
        self.socketio.emit('generate_text', data)

    def handle_personalities_list(self, data):
        personalities = data['personalities']
        self.personalities_list_received.emit(personalities)


    def handle_text_chunk(self, data):
        chunk = data['chunk']
        self.text_chunk_received.emit(chunk)

    def handle_text_generated(self, data):
        text = data['text']
        self.text_generated.emit(text)

    def handle_personalities_received(self, data):
        print("Received List of personalities")
        personalities = data['personalities']
        self.personalities = personalities
        self.personalities_received.emit(personalities)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("AIPersonality Client")

        self.user_input_layout = QHBoxLayout()
        self.user_text = QLineEdit()
        self.text_edit = QTextEdit()
        self.toolbar = QToolBar()
        self.submit_button = QPushButton("Submit")
        self.user_input_layout.addWidget(self.user_text)
        self.user_input_layout.addWidget(self.submit_button)

        self.statusbar = QStatusBar()
        self.personality_combo_box = QComboBox()
        self.personality_combo_box.setMinimumWidth(500)

        self.connect_action = QAction(QIcon(str(Path(__file__).parent/'assets/connected.svg')), "", self)
        self.connect_action.setCheckable(True)
        self.connect_action.toggled.connect(self.toggle_connection)

        self.toolbar.addAction(self.connect_action)
        self.toolbar.addWidget(self.personality_combo_box)
        self.addToolBar(self.toolbar)

        layout = QVBoxLayout()
        layout.addLayout(self.user_input_layout)
        layout.addWidget(self.text_edit)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.connector = ServerConnector()
        self.connector.text_chunk_received.connect(self.handle_text_chunk)
        self.connector.text_generated.connect(self.handle_text_generated)
        self.connector.connection_failed.connect(self.handle_connection_failed)
        self.connector.connection_status_changed.connect(self.handle_connection_status_changed)
        self.connector.personalities_received.connect(self.handle_personalities_received)
        self.connector.connect_to_server()

        self.submit_button.clicked.connect(self.submit_text)

        self.setStatusBar(self.statusbar)
        self.update_statusbar()

    @pyqtSlot(bool)
    def toggle_connection(self, checked):
        if checked:
            self.connector.connect_to_server()
            self.connect_action.setIcon(QIcon(str(Path(__file__).parent/'assets/connected.svg')))
        else:
            self.connector.disconnect_from_server()
            self.connect_action.setIcon(QIcon(str(Path(__file__).parent/'assets/disconnected.svg'))) 

    @pyqtSlot()
    def submit_text(self):
        prompt = self.user_text.text()
        self.selected_personality = self.personality_combo_box.currentText()
        self.text_edit.insertPlainText("User:"+prompt+"\n"+self.selected_personality+":")
        self.connector.generate_text(prompt)

    @pyqtSlot(str)
    def handle_text_chunk(self, chunk):
        self.text_edit.insertPlainText(chunk)

    @pyqtSlot(str)
    def handle_text_generated(self, text):
        pass#self.text_edit.append(text)

    @pyqtSlot()
    def handle_connection_failed(self):
        self.text_edit.append("Failed to connect to the server.")

    @pyqtSlot(bool)
    def handle_connection_status_changed(self, connected):
        if connected:
            self.statusbar.showMessage("Connected to the server")
        else:
            self.statusbar.showMessage("Disconnected from the server")

    @pyqtSlot(list)
    def handle_personalities_received(self, personalities):
        self.personality_combo_box.clear()
        self.personality_combo_box.addItems(personalities)

    def update_statusbar(self):
        if self.connector.connected:
            self.statusbar.showMessage("Connected to the server")
            self.connect_action.setIcon(QIcon(str(Path(__file__).parent/'assets/connected.svg')))
        else:
            self.statusbar.showMessage("Disconnected from the server")
            self.connect_action.setIcon(QIcon(str(Path(__file__).parent/'assets/disconnected.svg'))) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
