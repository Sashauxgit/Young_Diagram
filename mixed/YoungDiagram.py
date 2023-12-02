import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QWidget, QLabel,
    QTableWidgetItem, QMenuBar, QFileDialog, QColorDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor, QPixmap, QPainter, QBrush

class SecondWidget(QLabel):

    def workWithBackgroundColor(self):
        #self.setStyleSheet("background-color: rgba(255, 0, 0, 0.5)")
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255,0,0,125))
        self.setAutoFillBackground(True)
        self.setPalette(palette)


    def __init__(self, parent):
        super().__init__(parent)
        #self.workWithBackgroundColor()
        self.setGeometry(0, 0, 1500, 800)
        self.drowField = QPixmap(1500, 800)
        self.drowField.fill(QColor(255,0,0,125))
        self.setPixmap(self.drowField)

        painter = QPainter(self.pixmap())
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(500, 200, 5, 5)
        painter.end()
    '''    
    def mouseReleaseEvent(self, event):
        #print(event.pos())
        cell = self.parent().itemAt(event.pos().x(), event.pos().y())
        
        if cell.background().color() == self.parent().parent().noColor:
            cell.setBackground(self.parent().parent().curColor)
        else:
            cell.setBackground(self.parent().parent().noColor)
    '''
    def mouseMoveEvent(self, e):
        print(e.pos().x(), e.pos().y())
        painter = QPainter(self.pixmap())
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(e.pos().x(), e.pos().y(), 50, 50)
        painter.end()
        self.update()

class MainWindow(QMainWindow):
    def initSecondWindow(self):
        self.secondWindow = SecondWidget(self.table)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('YoungDraw')
        #self.setWindowIcon(QIcon('./assets/usergroup.png'))
        self.setGeometry(100, 100, 1100, 800)


        self.panel = QMenuBar(self)
        self.setMenuBar(self.panel)
        
        # Работа с меню
        menu = self.panel.addMenu("Menu")
        openAction = menu.addAction("Open diagram")
        saveAction = menu.addAction("Save diagram")
        screenAction = menu.addAction("Take screenshot")
        clearAction = menu.addAction("Clear field")

        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        screenAction.triggered.connect(self.takeScreenshot)
        clearAction.triggered.connect(self.clearTable)
        
        # Работа с палитрой
        paleteMenu = self.panel.addMenu("Palete")
        chooseColor = paleteMenu.addAction("Choose color")
        chooseColor.triggered.connect(self.openColorDialog)
        self.curColor = QColor(255,100,0)
        self.noColor = QColor(255,255,255)
        
        # Работа с таблицей
        self.table = QTableWidget(self)
        self.setCentralWidget(self.table)
        
        self.column_k = 300
        self.row_k = 300

        self.table.setColumnCount(self.column_k)
        self.table.setRowCount(self.row_k)
        
        for i in range(self.row_k):
            self.table.setRowHeight(i, 40)
        for i in range(self.column_k):
            self.table.setColumnWidth(i, 40)
        
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        
        self.table.cellClicked.connect(self.cell_clicked)
        self.table.doubleClicked.connect(self.cell_clicked)

        for i in range(self.row_k):
            for j in range(self.column_k):
                item = QTableWidgetItem(None)
                item.setBackground(self.noColor)
                # execute the line below to every item you need locked
                item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)
        
        self.initSecondWindow()
    
    def cell_clicked(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()
        if self.table.item(row, col).background().color() == self.noColor:
            self.table.item(row, col).setBackground(self.curColor)
        else:
            self.table.item(row, col).setBackground(self.noColor)
    
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Young Files (*.young)")
        if filename:
            try:
                self.clearTable()
                with open(filename, 'r') as file:
                    coords = file.read().split("\n")
                    if coords[-1] == '':
                        coords.pop()
                    for coord in coords:
                            row, col, r, g, b = tuple(map(int, coord.split(";")))
                            self.table.item(row, col).setBackground(QColor(r,g,b))
            except:
                raise ValueError("Incorrect file values")        
    
    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", ".", "Young Files (*.young)")
        if filename:
            with open(filename, 'w') as file:
                for row in range(self.row_k):
                    for col in range(self.column_k):
                        color = self.table.item(row, col).background().color()
                        r, g, b, _ = color.getRgb()
                        if color != self.noColor:
                            file.write("{};{};{};{};{}\n".format(row, col, r, g, b))
    
    def clearTable(self):
        for row in range(self.row_k):
            for col in range(self.column_k):
                self.table.item(row, col).setBackground(self.noColor)
    
    def takeScreenshot(self):
        screenshot = self.table.grab()
        filename, _ = QFileDialog.getSaveFileName(self, "Save screenshot", ".", "Image Files (*.png)")
        if filename:
            screenshot.save(filename, 'png')
    
    def openColorDialog(self):
        self.curColor = QColorDialog.getColor()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())