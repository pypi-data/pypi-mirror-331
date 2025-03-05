import sys
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, 
                             QVBoxLayout, QFileDialog, QMessageBox, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from kriptex.encryption import encrypt_file, decrypt_file

DEFAULT_URL = "https://raw.githubusercontent.com/Azccriminal/kriptex/main/symbol_external.txt"

class Kriptex(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kriptex")
        self.setGeometry(100, 100, 1000, 400)
        self.setStyleSheet("background-color: #f0d5b1;")

        self.symbols = []
        self.selected_symbols = []
        self.load_symbols(DEFAULT_URL)
        self.initUI()

    def load_symbols(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.symbols = response.text.strip().split(",")
                self.selected_symbols = [self.symbols[0]] * 10
            else:
                QMessageBox.warning(self, "Error", "Failed to load symbol file!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Connection error: {str(e)}")

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.symbol_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.url_layout = QHBoxLayout()
        self.length_layout = QHBoxLayout()
        self.sembol_labels = []

        self.url_input = QLineEdit(DEFAULT_URL)
        self.url_input.setPlaceholderText("Enter URL")
        self.url_input.returnPressed.connect(lambda: self.load_symbols(self.url_input.text()))
        self.url_layout.addWidget(QLabel("Symbol URL:"))
        self.url_layout.addWidget(self.url_input)
        self.main_layout.addLayout(self.url_layout)

        self.length_input = QLineEdit("16")  # Default key length
        self.length_input.setPlaceholderText("Key Length (e.g. 16, 24, 32)")
        self.length_layout.addWidget(QLabel("Key Length:"))
        self.length_layout.addWidget(self.length_input)
        self.main_layout.addLayout(self.length_layout)

        for i in range(10):
            vbox = QVBoxLayout()
            yukari_btn = QPushButton("▲")
            yukari_btn.clicked.connect(lambda _, j=i: self.change_symbol(j, 1))
            yukari_btn.setStyleSheet("background-color: #f0d5b1; color: black;")
            vbox.addWidget(yukari_btn)

            label = QLabel(self.symbols[0])
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 36))
            label.setStyleSheet("color: black;")
            vbox.addWidget(label)
            self.sembol_labels.append(label)

            asagi_btn = QPushButton("▼")
            asagi_btn.clicked.connect(lambda _, j=i: self.change_symbol(j, -1))
            asagi_btn.setStyleSheet("background-color: #f0d5b1; color: black;")
            vbox.addWidget(asagi_btn)

            self.symbol_layout.addLayout(vbox)

        self.main_layout.addLayout(self.symbol_layout)

        self.combo = QComboBox()
        self.combo.addItems(["AES", "RSA", "SHA256", "3DES"])  # Added "default" option
        self.button_layout.addWidget(self.combo)

        self.sifre_btn = QPushButton("Encrypt File")
        self.sifre_btn.clicked.connect(self.encrypt_file)
        self.sifre_btn.setStyleSheet("background-color: black; color: white;")
        self.button_layout.addWidget(self.sifre_btn)

        self.coz_btn = QPushButton("Decrypt File")
        self.coz_btn.clicked.connect(self.decrypt_file)
        self.coz_btn.setStyleSheet("background-color: black; color: white;")
        self.button_layout.addWidget(self.coz_btn)

        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def change_symbol(self, index, direction):
        current_index = self.symbols.index(self.selected_symbols[index])
        new_index = (current_index + direction) % len(self.symbols)
        self.selected_symbols[index] = self.symbols[new_index]
        self.sembol_labels[index].setText(self.symbols[new_index])

    def encrypt_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file:
            selected_algorithm = self.combo.currentText()
            key_length = int(self.length_input.text())
            with open(file, "r") as f:
                data = f.read()

            encrypted_data = encrypt_file(data, selected_algorithm, key_length, self.selected_symbols)

            with open(file + ".krt", "w") as f:
                f.write(encrypted_data)
            QMessageBox.information(self, "Success", "File encrypted successfully!")

    def decrypt_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Encrypted File")
        if file:
            selected_algorithm = self.combo.currentText()
            key_length = int(self.length_input.text())
            with open(file, "r") as f:
                encrypted_data = f.read()

            decrypted_data = decrypt_file(encrypted_data, selected_algorithm, key_length, self.selected_symbols)

            with open(file + ".dec", "w") as f:
                f.write(decrypted_data)
            QMessageBox.information(self, "Success", "File decrypted successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Kriptex()
    window.show()
    sys.exit(app.exec())
