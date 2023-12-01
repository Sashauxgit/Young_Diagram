import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QWidget,
    QTableWidgetItem, QMenuBar, QFileDialog, QColorDialog, QStyle
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor

class SecondWidget(QWidget):

    def workWithBackgroundColor(self):
        #self.setStyleSheet("background-color: rgba(255, 0, 0, 0.5)")
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255,0,0,125))
        self.setAutoFillBackground(True)
        self.setPalette(palette)


    def __init__(self, parent):
        super().__init__(parent)
        self.workWithBackgroundColor()
        self.setGeometry(0, 0, 1500, 800)
        
    def mouseReleaseEvent(self, event):
        #print(event.pos())
        cell = self.parent().itemAt(event.pos().x(), event.pos().y())
        
        if cell.background().color() == self.parent().noColor:
            cell.setBackground(self.parent().curColor)
        else:
            cell.setBackground(self.parent().noColor)


class CellTable(QTableWidget):
    def __init__(self, parent, curColor):
        super().__init__(parent)
        #self.table.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.table.size(), self.geometry()))

        self.column_k = 23
        self.row_k = 300

        self.curColor = curColor
        self.noColor = QColor(255,255,255)

        self.setColumnCount(self.column_k)
        self.setRowCount(self.row_k)
        
        for i in range(self.row_k):
            self.setRowHeight(i, 40)
        for i in range(self.column_k):
            self.setColumnWidth(i, 40)
        
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        
        self.cellClicked.connect(self.cell_clicked)
        self.doubleClicked.connect(self.cell_clicked)

        for i in range(self.row_k):
            for j in range(self.column_k):
                item = QTableWidgetItem(None)
                item.setBackground(self.noColor)
                # execute the line below to every item you need locked
                item.setFlags(Qt.ItemIsEnabled)
                self.setItem(i, j, item)
    
    def cell_clicked(self):
        row = self.currentRow()
        col = self.currentColumn()
        if self.item(row, col).background().color() == self.noColor:
            self.item(row, col).setBackground(self.curColor)
        else:
            self.item(row, col).setBackground(self.noColor)
    
    def cellWrite(self, row, column):
        color = self.item(row, column).background().color()
        r, g, b, _ = color.getRgb()
        if color != self.noColor:
            return "{};{};{};{};{}\n".format(row, column, r, g, b)
    
    def clearTable(self):
        for row in range(self.row_k):
            for col in range(self.column_k):
                self.item(row, col).setBackground(self.noColor)


class MainWindow(QMainWindow):
    def initSecondWindow(self):
        self.secondWindow = SecondWidget(self.pageTape[self.curPageInd])

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
        
        # Работа с палитрой
        paleteMenu = self.panel.addMenu("Palete")
        chooseColor = paleteMenu.addAction("Choose color")
        chooseColor.triggered.connect(self.openColorDialog)
        #self.curColor = QColor(255,100,0)
        #self.noColor = QColor(255,255,255)

        # Работа со страницами:
        pagesSwitching = self.panel.addMenu("Pages")
        toNextPageAct = pagesSwitching.addAction("go to next page")
        toBackPageAct = pagesSwitching.addAction("go to back page")
        toNextPageAct.triggered.connect(self.toNextPage)
        toBackPageAct.triggered.connect(self.toBackPage)
        
        self.curPageInd = 0
        self.pageTape = [CellTable(self, QColor(255,100,0))]
        self.setCentralWidget(self.pageTape[0])
        self.initSecondWindow()

        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        screenAction.triggered.connect(self.takeScreenshot)
        clearAction.triggered.connect(self.pageTape[self.curPageInd].clearTable)
    
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Young Files (*.young)")
        if filename:
            try:
                self.pageTape[self.curPageInd].clearTable()
                with open(filename, 'r') as file:
                    coords = file.read().split("\n")
                    if coords[-1] == '':
                        coords.pop()
                    for coord in coords:
                            row, col, r, g, b = tuple(map(int, coord.split(";")))
                            self.pageTape[self.curPageInd].item(row, col).setBackground(QColor(r,g,b))
            except:
                raise ValueError("Incorrect file values")        
    
    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", ".", "Young Files (*.young)")
        if filename:
            with open(filename, 'w') as file:
                for row in range(self.pageTape[self.curPageInd].row_k):
                    for col in range(self.pageTape[self.curPageInd].column_k):
                        cellInStr = self.pageTape[self.curPageInd].cellWrite(row, col)
                        if cellInStr != None:
                            file.write(cellInStr)
    
    def takeScreenshot(self):
        screenshot = self.pageTape[self.curPageInd].grab()
        filename, _ = QFileDialog.getSaveFileName(self, "Save screenshot", ".", "Image Files (*.png)")
        if filename:
            screenshot.save(filename, 'png')
    
    def openColorDialog(self):
        self.pageTape[self.curPageInd].curColor = QColorDialog.getColor()
    
    def toNextPage(self):
        self.pageTape[self.curPageInd].setHidden(True)
        self.curPageInd += 1
        
        if self.curPageInd == len(self.pageTape):
            self.pageTape.append(CellTable(self, QColor(255,100,0)))
        
        self.setCentralWidget(self.pageTape[self.curPageInd])
        self.pageTape[self.curPageInd].setHidden(False)
        self.update()

    def toBackPage(self):
        self.pageTape[self.curPageInd].setHidden(True)
        self.curPageInd -= 1
        
        if self.curPageInd == 0:
            return
        
        self.setCentralWidget(self.pageTape[self.curPageInd])
        self.pageTape[self.curPageInd].setHidden(False)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())