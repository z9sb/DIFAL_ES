from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6 import uic
from sys import argv
import sqlite3
import pandas as pd

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('untitled.ui', self)
        
        self.treeWidget.setHeaderLabels(
            ['PRODUTO', 'NCM', 'CEST', 'CFOP', 'UNIDADE', 'QUANTIDADE',
             'VALOR UNI. PRODUTP','VALOR TOTAL PRODUTO', 'ORIG', 'CST',
             'ALIQUOTA ICMS','VALOR ICMS', 'VALOR IPI', 'VALOR FRETE',
             'VALOR OUTRAS','VALOR DESCONTO', 'VALOR BC', 'VALOR ICMSDESC',
             'VALOR IMPOSTO'])
    
    def table_center(self):
        self.tree = QTreeWidgetItem(self.treeWidget)
        
        connec = sqlite3.connect('dados.db')
        result = pd.read_sql_query("SELECT * FROM Itens ", connec)
        result_list = result.values.tolist()
        
        self.x = ''
        
        for index, i in enumerate(result_list):
            if i[0] == self.x:
                QTreeWidgetItem(self.campo, index)
                
            else:
                self.tree = QTreeWidgetItem(self.treeWidget, index)
                self.tree.setText(0, i[2])
                self.tree.setCheckState(0, Qt.CheckState.Unchecked)
        
        self.treeWidget.expandAll()
        self.treeWidget.itemClicked.connect(self.printa)
        
    @pyqtSlot(QTreeWidgetItem, int)        
    def printa(self):
        return self.tree.setCheckState(0, Qt.CheckState.Checked)
        
if __name__ == '__main__':
    app = QApplication(argv)
    window = Ui()
    window.table_center()
    window.show()
    app.exec()