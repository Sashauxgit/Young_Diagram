import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, 
    QTableWidgetItem, QDockWidget, QFormLayout, 
    QLineEdit, QWidget, QPushButton, QSpinBox, 
    QMessageBox, QToolBar, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtGui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("GeeksCoders.com")
 
        # Create Open File button
        open_button = QPushButton("Open File", self)
        open_button.setGeometry(50, 50, 100, 30)
        open_button.clicked.connect(self.open_file)
 
        # Create Save File button
        save_button = QPushButton("Save File", self)
        save_button.setGeometry(50, 100, 100, 30)
        save_button.clicked.connect(self.take_screenshot)
 
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'r') as file:
                contents = file.read()
            print(contents)
 
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", ".", "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'w') as file:
                file.write("Welcome to GeeksCoders.com")
                file.write("Welcome to GeeksCoders.com")
    
    def take_screenshot(self):
        p = self.grab()
        p.save("screen.png", 'png')
 
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()