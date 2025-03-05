import sys
from PyQt6.QtWidgets import QApplication
from kriptex.kriptex_app import Kriptex  # Make sure you import your Kriptex class correctly
from kriptex.encryption import encrypt_file, decrypt_file

def main():
    app = QApplication(sys.argv)
    window = Kriptex()  # Create your Kriptex window object
    window.show()  # Display the window
    sys.exit(app.exec())  # Run the application's event loop

if __name__ == "__main__":
    main() 
