import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QWidget, QLabel, QPushButton, QTabWidget, QToolButton,
    QTableWidgetItem, QMenuBar, QFileDialog, QColorDialog, QStyle, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap, QPainter, QPen, QBrush


COLORS = [
'#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
'#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
'#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]


class SecondWidget(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(0, 0, 1500, 800)
        self.drowField = QPixmap(1500, 800)
        self.drowField.fill(QColor(0,0,0,0))
        self.setPixmap(self.drowField)

        self.pen = QPen()
        self.pen.setWidth(3)
        self.pen.setColor(self.parent().parent().parent().parent().parent().curColorForDrow)
        self.painter = QPainter(self.pixmap())
        self.painter.setPen(self.pen)
        self.painter.setRenderHint(QPainter.Antialiasing)

        self.last_x, self.last_y = None, None
    
    def mouseMoveEvent(self, e):
        if self.parent().parent().parent().parent().parent().workWithCellField:
            if e.buttons() == Qt.LeftButton:
                self.parent().fillCell(e)
            if e.buttons() == Qt.RightButton:
                self.parent().unfillCell(e)
            return
        
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.

        self.painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        #self.painter.end()
        self.update()

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        if self.parent().parent().parent().parent().parent().workWithCellField:
            if e.button() == Qt.LeftButton:
                self.parent().fillCell(e)
            if e.button() == Qt.RightButton:
                self.parent().unfillCell(e)
        else:
            self.last_x = None
            self.last_y = None


class QPaletteButton(QPushButton):
    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QSize(24,24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)


class CellTable(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        #self.table.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.table.size(), self.geometry()))

        self.column_k = 23
        self.row_k = 14

        self.setColumnCount(self.column_k)
        self.setRowCount(self.row_k)
        
        for i in range(self.row_k):
            self.setRowHeight(i, 40)
        for i in range(self.column_k):
            self.setColumnWidth(i, 40)
        
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        for i in range(self.row_k):
            for j in range(self.column_k):
                item = QTableWidgetItem(None)
                item.setBackground(self.parent().parent().parent().noColor)
                # execute the line below to every item you need locked
                item.setFlags(Qt.ItemIsEnabled)
                self.setItem(i, j, item)
        
        self.setFocusPolicy(Qt.NoFocus)
    
    def cellWrite(self, row, column):
        color = self.item(row, column).background().color()
        r, g, b, _ = color.getRgb()
        if color != self.parent().parent().parent().noColor:
            return "{};{};{};{};{}\n".format(row, column, r, g, b)
    
    def clearTable(self):
        for row in range(self.row_k):
            for col in range(self.column_k):
                self.item(row, col).setBackground(self.parent().parent().parent().noColor)
    
    def fillCell(self, event):
        cell = self.itemAt(event.pos().x(), event.pos().y())  
        cell.setBackground(self.parent().parent().parent().parent().curColorForCell)

    
    def unfillCell(self, event):
        cell = self.itemAt(event.pos().x(), event.pos().y())  
        cell.setBackground(self.parent().parent().parent().parent().noColor)


class MainWindow(QMainWindow):
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
        self.clearAction = menu.addAction("Clear field")
        
        # Работа с палитрой
        paleteMenu = self.panel.addMenu("Palete")
        chooseColor = paleteMenu.addAction("Choose color")
        chooseColor.triggered.connect(self.openColorDialog)
        self.curColorForCell = QColor(255,100,0)
        self.curColorForDrow = QColor(0,0,0)
        self.noColor = QColor(255,255,255)

        # Работа с лайаутами
        self.mainWidget = QWidget(self)
        self.lay = QVBoxLayout(self.mainWidget)
        self.mainWidget.setLayout(self.lay)

        # Работа со страницами:
        self.curPageInd = 0
        self.pageTape = QTabWidget(self.mainWidget)
        self.lay.addWidget(self.pageTape)
        #self.pageTape.setTabsClosable(True)

        self.tabButton = QToolButton(self)
        self.tabButton.setText('+')
        font = QFont("Times new roman", 30)
        font.setBold(True)
        self.tabButton.setFont(font)
        self.pageTape.setCornerWidget(self.tabButton)
        self.tabButton.clicked.connect(self.addPage)

        self.pageTape.currentChanged.connect(self.changePage)
        self.pageTape.addTab(CellTable(self.pageTape), 'Страница {}'.format(self.curPageInd + 1))
        self.secondWindows = [SecondWidget(self.curPage())]

        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        screenAction.triggered.connect(self.takeScreenshot)
        self.clearAction.triggered.connect(self.curPage().clearTable)

        palitra = QHBoxLayout()
        self.add_palette_buttons(palitra)
        self.lay.addLayout(palitra)
        self.setCentralWidget(self.mainWidget)

        self.workWithCellField = False
        self.addFlag = False

    
    def set_pen_color(self, c):
        pen = QPen()
        pen.setWidth(3)
        color = QColor(c)
        pen.setColor(color)
        self.curColorForDrow = color
        self.secondWindows[self.curPageInd].painter.end()
        self.secondWindows[self.curPageInd].painter = QPainter(self.secondWindows[self.curPageInd].pixmap())
        self.secondWindows[self.curPageInd].painter.setPen(pen)
        self.secondWindows[self.curPageInd].painter.setRenderHint(QPainter.Antialiasing)

    def add_palette_buttons(self, layout):
        for c in COLORS:
            b = QPaletteButton(c)
            b.pressed.connect(lambda c=c: self.set_pen_color(c))
            layout.addWidget(b)
    
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Young Files (*.young)")
        if filename:
            try:
                self.curPage().clearTable()
                with open(filename, 'r') as file:
                    coords = file.read().split("\n")
                    if coords[-1] == '':
                        coords.pop()
                    for coord in coords:
                            row, col, r, g, b = tuple(map(int, coord.split(";")))
                            self.curPage().item(row, col).setBackground(QColor(r,g,b))
            except:
                raise ValueError("Incorrect file values")        
    
    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", ".", "Young Files (*.young)")
        if filename:
            with open(filename, 'w') as file:
                for row in range(self.curPage().row_k):
                    for col in range(self.curPage().column_k):
                        cellInStr = self.curPage().cellWrite(row, col)
                        if cellInStr != None:
                            file.write(cellInStr)
    
    def takeScreenshot(self):
        screenshot = self.curPage().grab()
        filename, _ = QFileDialog.getSaveFileName(self, "Save screenshot", ".", "Image Files (*.png)")
        if filename:
            screenshot.save(filename, 'png')
    
    def openColorDialog(self):
        self.curColorForCell = QColorDialog.getColor()
    
    def addPage(self):
        self.addFlag = True
        self.pageTape.addTab(CellTable(self.pageTape), 'Страница {}'.format(self.pageTape.count() + 1))
        self.pageTape.setCurrentIndex(self.pageTape.count() - 1)
        self.secondWindows.append(SecondWidget(self.curPage()))
        self.secondWindows[-1].show()
        self.addFlag = False

    def changePage(self):
        self.clearAction.triggered.disconnect(self.curPage().clearTable)
        self.curPageInd = self.pageTape.currentIndex()
        self.clearAction.triggered.connect(self.curPage().clearTable)
        if not self.addFlag:
            self.set_pen_color(self.curColorForDrow)
    
    def curPage(self):
        return self.pageTape.widget(self.curPageInd)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_S:
            self.workWithCellField = not self.workWithCellField

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())