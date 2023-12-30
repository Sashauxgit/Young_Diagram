import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QWidget, QLabel, QPushButton, QTabWidget, QToolButton, QMessageBox,
QTableWidgetItem, QMenuBar, QFileDialog, QColorDialog, QStyle, QVBoxLayout, QHBoxLayout, QSlider, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMouseEvent, QPalette, QColor, QFont, \
QPixmap, QPainter, QPen, QBrush, QIntValidator, QCursor

import traceback as tr
from fpdf import FPDF
from os import remove


def exception_hook(type, message, tb):
    er = QMessageBox(window)
    er.setWindowTitle("Ошибка")
    er.setText("An unexpected error occurred in the program! Detalis:\n"
f"\nStack:\n{''.join(tr.format_list(tr.extract_tb(tb)))}\n"
f"Error type: {type}\n"
f"Error message: {message}\n\n"
"The data could be lost! Do you want to save it?")
    er.setStandardButtons(QMessageBox.Save | QMessageBox.Ignore)
    er.setIcon(QMessageBox.Critical)
    reply = er.exec()
    if reply == QMessageBox.Save:
        window.saveFile()

sys.excepthook = exception_hook


COLORS = [
'#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
'#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
'#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]

class NumLineEdit(QLineEdit):
    def __init__(self, parent, coord_x, coord_y, text):
        super().__init__(parent)
        self.setGeometry(coord_x, coord_y, 40, 30)
        self.setFont(QFont("Times new roman", 20))
        validator = QIntValidator(0, 99, self)
        self.setValidator(validator)

        self.coord_x = coord_x
        self.coord_y = coord_y

        self.setText(text)

        self.setFocus()
        self.show()
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.parent().parent().setTextCell(self.coord_x, self.coord_y, self.text())
            self.parent().parent().update()
            self.parent().update()
            self.close()
        elif e.key() == Qt.Key_Escape:
            self.parent().update()
            self.close()
        else:
            super().keyPressEvent(e)


class SecondWidget(QLabel):
    def __init__(self, parent, data = None):
        super().__init__(parent)
        self.setGeometry(0, 0, 1500, 800)
        self.drowField = QPixmap(1500, 800)
        self.drowField.fill(QColor(0,0,0,0))
        self.setPixmap(self.drowField)
        self.painter = None
        self.createPainter(self.parent().parent().parent().parent().parent().curColor, \
self.parent().parent().parent().parent().parent().curThickness)

        self.setFocus()

        self.last_x, self.last_y = None, None
        self.editLine = None

        self.paintingForSave = []

        if data != None:
            self.loadPaint(data)
    
    def loadPaint(self, data):
        vecs = data.split("\n")
        for vec in vecs:
            coords = vec[1:len(vec) - 1].split("), ")
            if len(coords) > 1:
                color = coords[-1][1:len(coords[-1]) - 1].split(", ")
                thickness = int(color[3])
                color = QColor(int(color[0]), int(color[1]), int(color[2]))
                coords = coords[0:len(coords) - 1]

                for coord in coords:
                    coord = coord[1:].split(", ")
                    self.createPainter(color, thickness)
                    self.toPaint(int(coord[0]), int(coord[1]))
                self.last_x = None
                self.last_y = None
                self.paintingForSave[-1].append((color.red(), color.green(), color.blue(), thickness))
        
        self.createPainter(self.parent().parent().parent().parent().parent().curColor, \
self.parent().parent().parent().parent().parent().curThickness)
        self.update()
    
    def redrow(self, data):
        for vec in data:
            color = QColor(vec[-1][0], vec[-1][1], vec[-1][2])
            coords = vec[:-1]
            for coord in coords:
                self.createPainter(color, vec[-1][3])
                self.toPaint(coord[0], coord[1])
            self.last_x = None
            self.last_y = None
            self.paintingForSave[-1].append((color.red(), color.green(), color.blue(), vec[-1][3]))
        
        self.createPainter(self.parent().parent().parent().parent().parent().curColor, \
self.parent().parent().parent().parent().parent().curThickness)
        self.update()
    
    def toPaint(self, x, y):
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            line = [(self.last_x, self.last_y)]
            self.paintingForSave.append(line)
            return

        self.painter.drawLine(self.last_x, self.last_y, x, y)
        self.paintingForSave[-1].append((x, y))
        #self.painter.end()
        self.update()

        self.last_x = x
        self.last_y = y
    
    def createPainter(self, color, thickness):
        pen = QPen()
        pen.setWidth(thickness)
        color = QColor(color)
        pen.setColor(color)

        if self.painter != None:
            self.painter.end()
        
        self.painter = QPainter(self.pixmap())
        self.painter.setPen(pen)
        self.painter.setRenderHint(QPainter.Antialiasing)
    
    def mouseMoveEvent(self, e):
        if self.parent().parent().parent().parent().parent().workWithCellField:
            if e.buttons() == Qt.LeftButton:
                self.parent().fillCell(e)
            if e.buttons() == Qt.RightButton:
                self.parent().unfillCell(e)
            self.setFocus()
            return
        
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            line = [(self.last_x, self.last_y)]
            self.paintingForSave.append(line)
            self.setFocus()
            return # Ignore the first time.

        self.painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        self.paintingForSave[-1].append((e.x(), e.y()))
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
        elif self.last_x != None and self.last_y != None:
            self.last_x = None
            self.last_y = None

            if len(self.paintingForSave) > 0:
                c = self.parent().parent().parent().parent().parent().curColor
                self.paintingForSave[-1].append((c.red(), c.green(), c.blue(), self.parent().parent().parent().parent().parent().curThickness))
    
    def wheelEvent(self, e):
        workSpace = self.parent().parent().parent().parent().parent()
        if e.angleDelta().y() > 0:
            newInd = workSpace.curPageInd - 1
        else:
            newInd = workSpace.curPageInd + 1
        
        if newInd >= 0 or newInd < workSpace.pageTape.count():
            workSpace.pageTape.setCurrentIndex(newInd)
    
    def keyPressEvent(self, e):
        workSpace = self.parent().parent().parent().parent().parent()
        if e.key() == Qt.Key_Up or e.key() == Qt.Key_Down:
            workSpace.switchMode()
        
        if e.key() == Qt.Key_Left and workSpace.curPageInd > 0:
            workSpace.pageTape.setCurrentIndex(workSpace.curPageInd - 1)
        
        if e.key() == Qt.Key_Right and workSpace.curPageInd < workSpace.pageTape.count() - 1:
            workSpace.pageTape.setCurrentIndex(workSpace.curPageInd + 1)

        numKeys = {Qt.Key_1: '1', Qt.Key_2: '2', Qt.Key_3: '3', Qt.Key_4: '4', Qt.Key_5: '5',
Qt.Key_6: '6', Qt.Key_7: '7', Qt.Key_8: '8', Qt.Key_9: '9', Qt.Key_0: '0'}
        
        if e.key() in numKeys:
            if self.editLine != None:
                self.editLine.close()
            cursor = QCursor()
            position = self.mapFromGlobal(cursor.pos())
            self.editLine = NumLineEdit(self, position.x(), position.y(), numKeys[e.key()])
        
        if e.key() == Qt.Key_Z and len(self.paintingForSave) > 0:
            workSpace.ctrl_Z(self.paintingForSave[-1], self.paintingForSave[:-1])
        
        if e.key() == Qt.Key_X:
            self.parent().ctrl_X()
        
        if e.key() == Qt.Key_U:
            self.parent().ctrl_U()
        
        if e.key() == Qt.Key_Y:
            self.parent().parent().parent().parent().parent().ctrl_Y(self.paintingForSave)

    
    def update(self):
        self.setFocus()
        super().update()



class QPaletteButton(QPushButton):
    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QSize(24,24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)


class CellTable(QTableWidget):
    def __init__(self, parent, initData = None):
        super().__init__(parent)
        #self.table.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.table.size(), self.geometry()))

        self.column_k = 59
        self.row_k = 27

        self.setColumnCount(self.column_k)
        self.setRowCount(self.row_k)
        
        #for i in range(self.row_k):
        #    self.setRowHeight(i, 30)
        #for i in range(self.column_k):
        #    self.setColumnWidth(i, 50)
        
        self.horizontalHeader().setMinimumSectionSize(30)
        self.horizontalHeader().setDefaultSectionSize(32)
        self.horizontalHeader().hide()
        
        self.verticalHeader().setMinimumSectionSize(30)
        self.verticalHeader().setDefaultSectionSize(32)
        self.verticalHeader().hide()

        for i in range(self.row_k):
            for j in range(self.column_k):
                item = QTableWidgetItem(None)
                item.setBackground(self.parent().parent().parent().noColor)
                item.setFont(QFont("Times new roman", 15))
                item.setTextAlignment(Qt.AlignCenter)
                # execute the line below to every item you need locked
                item.setFlags(Qt.ItemIsEnabled)
                self.setItem(i, j, item)
        
        self.setFocusPolicy(Qt.NoFocus)

        if initData != None:
            self.init(initData)
        
        self.cellEventsZ = []
        self.cellEventsY = []
    
    def init(self, data):
        coords = data.split("\n")
        if coords[-1] == '':
            coords.pop()
            for coord in coords:
                row, col, r, g, b = tuple(map(int, coord.split(";")[:-1]))
                self.item(row, col).setBackground(QColor(r,g,b))

                text = coord.split(";")[-1]
                if text != None and text != '':
                    self.item(row, col).setText(str(text))
    
    def cellWrite(self, row, column):
        color = self.item(row, column).background().color()
        r, g, b, _ = color.getRgb()
        if color != self.parent().parent().parent().parent().noColor or self.item(row, column).text() != "":
            return "{};{};{};{};{};{}\n".format(row, column, r, g, b, self.item(row, column).text())
    
    def clearTable(self):
        for row in range(self.row_k):
            for col in range(self.column_k):
                self.item(row, col).setBackground(self.parent().parent().parent().parent().noColor)
                self.item(row, col).setText('')
    
    def fillCell(self, event):
        cell = self.itemAt(event.pos().x(), event.pos().y())
        if cell != None and cell.background().color() != self.parent().parent().parent().parent().curColor:
            self.cellEventsZ.append((event.pos().x(), event.pos().y(), cell.background().color(), cell.text()))
            cell.setBackground(self.parent().parent().parent().parent().curColor)
            self.cellEventsY = []

    def setTextCell(self, x, y, text):
        cell = self.itemAt(x, y)
        if cell != None:
            self.cellEventsZ.append((x, y, cell.background().color(), cell.text()))
            cell.setText(text)
            self.cellEventsY = []
    
    def unfillCell(self, event):
        cell = self.itemAt(event.pos().x(), event.pos().y())
        if cell != None and cell.background().color() != self.parent().parent().parent().parent().noColor:
            self.cellEventsZ.append((event.pos().x(), event.pos().y(), cell.background().color(), cell.text()))  
            cell.setBackground(self.parent().parent().parent().parent().noColor)
            self.cellEventsY = []
    
    def ctrl_X(self):
        if len(self.cellEventsZ) > 0:
            do = self.cellEventsZ[-1]
            self.cellEventsZ = self.cellEventsZ[:-1]
            cell = self.itemAt(do[0], do[1])
            self.cellEventsY.append((do[0], do[1], cell.background().color(), cell.text()))
            cell.setBackground(do[2])
            cell.setText(do[3])
            self.update()
    
    def ctrl_U(self):
        if len(self.cellEventsY) > 0:
            do = self.cellEventsY[-1]
            self.cellEventsY = self.cellEventsY[:-1]
            cell = self.itemAt(do[0], do[1])
            self.cellEventsZ.append((do[0], do[1], cell.background().color(), cell.text()))
            cell.setBackground(do[2])
            cell.setText(do[3])
            self.update()

class ThickDialog(QDialog):
    def closeEvent(self, e):
        self.parent().demoPainter.end()
        self.parent().set_pen_color(self.parent().curColor)
        e.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YoungDraw')
        #self.setWindowIcon(QIcon('./assets/usergroup.png'))
        self.setGeometry(100, 100, 1100, 800)

        self.workWithCellField = False
        self.addFlag = True
        self.reserveData = []

        self.panel = QMenuBar(self)
        self.setMenuBar(self.panel)
        
        # Работа с меню
        menu = self.panel.addMenu("Menu")
        openAction = menu.addAction("Open diagram")
        saveAction = menu.addAction("Save diagram")
        exportPdfAction = menu.addAction("Export to PDF")
        self.clearAction = menu.addAction("Clear current page")
        self.resetAction = menu.addAction("Full reset pages")
        
        # Работа с палитрой
        paramsMenu = self.panel.addMenu("Display parameters")
        chooseColor = paramsMenu.addAction("Choose color")
        chooseColor.triggered.connect(self.openColorDialog)

        chooseThickness = paramsMenu.addAction("Choose pen thickness")
        chooseThickness.triggered.connect(self.openThicknessDialog)

        self.switchToCellAct = self.panel.addAction("Drow mode")
        self.switchToCellAct.triggered.connect(self.switchMode)

        self.curThickness = 3
        self.curColor = QColor(0,0,0)
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
        exportPdfAction.triggered.connect(self.exportPDF)
        self.clearAction.triggered.connect(self.clearField)
        self.resetAction.triggered.connect(self.fullReset)

        palitra = QHBoxLayout()
        self.add_palette_buttons(palitra)
        self.lay.addLayout(palitra)
        self.setCentralWidget(self.mainWidget)

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        self.setCursor(cursor)

        self.addFlag = False

    def set_color(self, c):
        self.curColor = QColor(c)
        self.set_pen_color(c)

    def set_pen_color(self, c, workSpace = None):
        pen = QPen()
        pen.setWidth(self.curThickness)
        color = QColor(c)
        pen.setColor(color)

        if workSpace == None:
            self.curColor = color
            workSpace = self.secondWindows[self.curPageInd]
        workSpace.painter.end()
        workSpace.painter = QPainter(workSpace.pixmap())
        workSpace.painter.setPen(pen)
        workSpace.painter.setRenderHint(QPainter.Antialiasing)

    def add_palette_buttons(self, layout):
        for c in COLORS:
            b = QPaletteButton(c)
            b.pressed.connect(lambda c=c: self.set_color(c))
            layout.addWidget(b)
    
    def openFile(self):
        if not self.saveQuestion():
            return

        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Young Files (*.young)")
        if filename:
            try:
                self.fullReset(ask = "noAsk")
                with open(filename, 'r') as file:
                    pageValues = file.read().split("---\n---\n")
                    pageValues.remove('')
                    for page in pageValues:
                        parts = page.split("\n\n")
                        self.addPage(parts[0], parts[1], 0)
                
                self.pageTape.removeTab(0)
                self.secondWindows.pop(0)
                    
            except:
                er = QMessageBox(self)
                er.setWindowTitle("Ошибка")
                er.setText("Ошибка чтения файла. Файл некорректен.")
                er.setStandardButtons(QMessageBox.Ok)
                er.setIcon(QMessageBox.Critical)
                er.exec()       
    
    def saveFile(self):
        self.secondWindows[self.curPageInd].setFocus()
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", ".", "Young Files (*.young)")
        if filename:
            with open(filename, 'w') as file:
                # self.pageTape.widget(i)
                # self.secondWindows[i]
                for i in range(self.pageTape.count()):
                    for vec in self.secondWindows[i].paintingForSave:
                        file.write(str(vec))
                        file.write("\n")
                    file.write("\n")
                    if len(self.secondWindows[i].paintingForSave) == 0:
                        file.write("\n")
                    for row in range(self.pageTape.widget(i).row_k):
                        for col in range(self.pageTape.widget(i).column_k):
                            cellInStr = self.pageTape.widget(i).cellWrite(row, col)
                            if cellInStr != None:
                                file.write(cellInStr)
                    file.write("---\n---\n")
                #file.write("EOF")
            return True
        return False
    
    def exportPDF(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to PDF", ".", "PDF Files (*.pdf)")
        if filename:
            if '.pdf' not in filename:
                filename += '.pdf'

            for i in range(len(self.secondWindows)):
                img = self.pageTape.widget(i).grab()
                img.save(f"young_reserve_page_picture_{i}.png")
            
            pdf = FPDF()
            for i in range(len(self.secondWindows)):
                pdf.add_page('landscape', (float(self.curPage().height()), float(self.curPage().width())))
                pdf.image(f"young_reserve_page_picture_{i}.png", h = self.curPage().height(), w = self.curPage().width())
                remove(f"young_reserve_page_picture_{i}.png")

            pdf.output(filename)
            return True
        return False
    
    def ctrl_Z(self, dataForY, data):
        self.reserveData.append(dataForY)
        self.secondWindows[self.curPageInd].close()
        self.secondWindows[self.curPageInd] = SecondWidget(self.curPage())
        self.secondWindows[self.curPageInd].redrow(data)
        self.secondWindows[self.curPageInd].show()
    
    def ctrl_Y(self, data):
        if len(self.reserveData) > 0:
            data.append(self.reserveData[-1])
            self.reserveData.pop()
            self.secondWindows[self.curPageInd].close()
            self.secondWindows[self.curPageInd] = SecondWidget(self.curPage())
            self.secondWindows[self.curPageInd].redrow(data)
            self.secondWindows[self.curPageInd].show()
    
    def clearField(self, ask):
        if ask != "noAsk" and not self.saveQuestion():
            return

        self.curPage().clearTable()
        self.secondWindows[self.curPageInd].close()
        self.secondWindows[self.curPageInd] = SecondWidget(self.curPage())
        self.secondWindows[self.curPageInd].show()
        self.secondWindows[self.curPageInd].setFocus()
    
    def fullReset(self, ask):
        if ask != "noAsk" and not self.saveQuestion():
            return

        self.pageTape.setCurrentIndex(0)
        pageCount = self.pageTape.count()
        for i in range(1, pageCount):
            self.pageTape.removeTab(1)
            self.secondWindows.pop(1)
        
        self.clearField(ask = "noAsk")

    def openColorDialog(self):
        self.curColor = QColorDialog.getColor()
        self.set_pen_color(self.curColor)
    
    def openThicknessDialog(self):
        self.thickDialog = ThickDialog(self)
        self.thickDialog.setWindowTitle('Pen thickness choosing')
        self.thickDialog.setGeometry(225, 200, 900, 400)

        sliderPlace = QWidget(self.thickDialog)
        sliderPlace.setFixedHeight(70)
        self.slider = QSlider(Qt.Orientation.Horizontal, sliderPlace)
        self.slider.move(100, 35)
        self.slider.setFixedWidth(800)
        self.slider.setRange(1, 15)
        self.slider.setValue(self.curThickness)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.updateThickness)

        dialogLayout = QVBoxLayout(self.thickDialog)
        dialogLayout.addWidget(sliderPlace)
        
        self.demoLabel = QLabel(self.thickDialog)
        pixmap = QPixmap(1000, 130)
        pixmap.fill(QColor(0,0,0,0))
        self.demoLabel.setPixmap(pixmap)
        
        pen = QPen()
        pen.setWidth(self.curThickness)
        pen.setColor(self.curColor)
        
        self.demoPainter = QPainter(self.demoLabel.pixmap())
        self.demoPainter.setPen(pen)
        self.demoPainter.setRenderHint(QPainter.Antialiasing)
        self.demoPainter.drawPoint(500, 20)

        dialogLayout.addWidget(self.demoLabel)
        self.thickDialog.setLayout(dialogLayout)
        self.thickDialog.show()
    
    def updateThickness(self):
        self.curThickness = self.slider.value()

        self.demoLabel.pixmap().fill(QColor(0,0,0,0))
        
        pen = QPen()
        pen.setWidth(self.curThickness)
        pen.setColor(self.curColor)
        
        self.demoPainter.setPen(pen)
        self.demoPainter.drawPoint(500, 20)
        self.thickDialog.update()

    
    def addPage(self, drowData = None, cellData = None, pageNumPolicy = 1):
        self.addFlag = True
        self.pageTape.addTab(CellTable(self.pageTape, cellData), 'Страница {}'.format(self.pageTape.count() + pageNumPolicy))
        self.pageTape.setCurrentIndex(self.pageTape.count() - 1)
        if type(drowData) == bool:
            drowData = None
        self.secondWindows.append(SecondWidget(self.curPage(), drowData))
        self.secondWindows[-1].show()
        self.setFocus()
        self.addFlag = False

    def changePage(self):
        self.curPageInd = self.pageTape.currentIndex()
        #print(self.curPageInd) #
        if not self.addFlag:
            self.set_pen_color(self.curColor)
        self.setFocus()
    
    def curPage(self):
        return self.pageTape.widget(self.curPageInd)
    
    def switchMode(self):
        self.workWithCellField = not self.workWithCellField
        if self.workWithCellField:
            self.switchToCellAct.setText("Young mode")
            cursor = QCursor()
            cursor.setShape(Qt.PointingHandCursor)
            self.setCursor(cursor)
        else:
            cursor = QCursor()
            cursor.setShape(Qt.CrossCursor)
            self.setCursor(cursor)
            self.switchToCellAct.setText("Drow mode")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Up or e.key() == Qt.Key_Down:
            self.switchMode()
        
        if e.key() == Qt.Key_Left and self.curPageInd > 0:
            self.pageTape.setCurrentIndex(self.curPageInd - 1)
        
        if e.key() == Qt.Key_Right and self.curPageInd < self.pageTape.count() - 1:
            self.pageTape.setCurrentIndex(self.curPageInd + 1)
        
        if e.key() == Qt.Key_Z and len(self.secondWindows[self.curPageInd].paintingForSave) > 0:
            self.ctrl_Z(self.secondWindows[self.curPageInd].paintingForSave[-1], self.secondWindows[self.curPageInd].paintingForSave[:-1])
        
        if e.key() == Qt.Key_X:
            self.curPage().ctrl_X()
        
        if e.key() == Qt.Key_U:
            self.curPage().ctrl_U()
        
        if e.key() == Qt.Key_Y:
            self.ctrl_Y(self.secondWindows[self.curPageInd].paintingForSave)

        numKeys = {Qt.Key_1: '1', Qt.Key_2: '2', Qt.Key_3: '3', Qt.Key_4: '4', Qt.Key_5: '5',
Qt.Key_6: '6', Qt.Key_7: '7', Qt.Key_8: '8', Qt.Key_9: '9', Qt.Key_0: '0'}
        
        if e.key() in numKeys:
            workSpace = self.secondWindows[self.curPageInd]
            if workSpace.editLine != None:
                workSpace.editLine.close()
            cursor = QCursor()
            position = workSpace.mapFromGlobal(cursor.pos())
            workSpace.editLine = NumLineEdit(workSpace, position.x(), position.y(), numKeys[e.key()])
    
    def saveQuestion(self):

        reply = QMessageBox.question(self,\
            'Young diagram redactor',\
            "The data could be lost! Do you want to continue?",\
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            return True
        else:
            return False
    
    def closeEvent(self, e):
        if self.saveQuestion():
            self.secondWindows[self.curPageInd].painter.end()
            e.accept()
        else:
            e.ignore()
            self.setFocus()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())