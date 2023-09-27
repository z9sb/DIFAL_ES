import sqlite3
from sys import argv

import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem

from funcoes import calculo_diferencial_icms
from emitir_dua import Dua
import bd
from datetime import datetime


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('untitled.ui', self)
        self.init_ui()

    def init_ui(self):
        self.empresas.itemClicked.connect(self.busca_empresa)
        self.notas.itemClicked.connect(self.busca_notas)

        self.btn_empresas.clicked.connect(self.btn_table_empresas)
        self.btn_itens.clicked.connect(self.btn_table_itens)
        self.btn_notas.clicked.connect(self.btn_table_notas)
        self.btn_itens_salvar.clicked.connect(self.calculo_imposto)
        self.btn_itens_dua.clicked.connect(self.emitir_dua)
        self.btn_itens_mt.clicked.connect(self.select_all)
        self.btn_itens_dt.clicked.connect(self.mark_off_all)
        self.btn_itens_zt.clicked.connect(self.zerar_imposto)
        self.btn_itens_cps.clicked.connect(self.check_selection_pre)

        self.itens.setHeaderLabels(
            ['PRODUTO', 'NCM', 'CEST', 'CFOP', 'UNIDADE', 'QUANTIDADE',
             'VALOR UNI. PRODUTO', 'VALOR TOTAL PRODUTO', 'ORIG', 'CST',
             'ALIQUOTA ICMS', 'VALOR ICMS', 'VALOR IPI', 'VALOR FRETE',
             'VALOR OUTRAS', 'VALOR DESCONTO', 'VALOR IMPOSTO'])

    def table_home(self):
        self.tree = QTreeWidgetItem(self.empresas)

        self.connec = sqlite3.connect('dados.db')
        self.conn = self.connec.cursor()
        empresa_table = self.conn.execute(
            "SELECT CNPJ, Nome FROM Empresas ").fetchall()

        self.elemento = ''

        for index, value in enumerate(empresa_table):
            if value[0] == self.elemento:
                QTreeWidgetItem(self.campo, index)

            else:
                self.tree = QTreeWidgetItem(self.empresas, index)
                self.tree.setText(0, value[1])
                self.tree.setText(1, value[0])
                self.tree.setCheckState(0, Qt.CheckState.Unchecked)

        self.empresas.expandAll()

    def btn_table_empresas(self):
        return self.stackedWidget.setCurrentWidget(self.table_empresas)

    def btn_table_itens(self):
        return self.stackedWidget.setCurrentWidget(self.table_itens)

    def btn_table_notas(self):
        return self.stackedWidget.setCurrentWidget(self.table_notas)

    def set_notas(self, empresa_id):
        result = pd.read_sql_query(
            "SELECT Chave, DataEmissao, NomeFornecedor "
            "FROM NotasFiscais WHERE EmpresaID = ?",
            self.connec, params=(empresa_id,)
        )
        result_list = result.values.tolist()
        self.notas.clear()

        for index, i in enumerate(result_list):
            if i[0] == self.elemento:
                QTreeWidgetItem(self.campo, index)

            else:
                self.tree = QTreeWidgetItem(self.notas, index)

                for index, item in enumerate(i):
                    self.tree.setText(index, item)

                self.tree.setCheckState(0, Qt.CheckState.Unchecked)

        self.notas.expandAll()

    def table_center(self, NotaFiscalID):
        self.tree = QTreeWidgetItem(self.itens)
        self.itens.clear()

        result_list = bd.seek_id_nf_item(NotaFiscalID)

        empresa_id = self.conn.execute(
            "SELECT ID FROM Empresas WHERE CNPJ = ?", (self.cnpj_dest,)).fetchone()

        nf_id = self.conn.execute(
            "SELECT ID FROM NotasFiscais WHERE EmpresaID = ?",
            (empresa_id[0],)).fetchall()

        all_items = []

        for nf in nf_id:
            nota_id = self.conn.execute(
                "SELECT NomeProduto FROM Itens WHERE ValorImposto > 0 AND NotaFiscalID = ?",
                (nf[0],)).fetchall()

            if nota_id:
                for item in nota_id:
                    all_items.append(item[0])

        for index, valor in enumerate(result_list):
            if valor[0] == self.elemento:
                QTreeWidgetItem(self.campo, index)

            else:
                self.tree = QTreeWidgetItem(self.itens, index)
                for index, item in enumerate(valor):
                    self.tree.setText(index, str(item))

                self.tree.setCheckState(0, Qt.CheckState.Unchecked)

                for index, item in enumerate(valor):
                    if index == 0 and item in all_items:
                        self.tree.setCheckState(
                            0, Qt.CheckState.PartiallyChecked)

        self.itens.expandAll()
        self.somar_imposto()
        
    def busca_empresa(self):
        try:
            for item in range(self.empresas.topLevelItemCount()):
                tree = self.empresas.topLevelItem(item)
                self.cnpj = tree.text(1)
                self.nome = tree.text(0)
                check = tree.checkState(0).value

                if check == 2:
                    self.cnpj_dest = self.cnpj
                    self.stackedWidget.setCurrentWidget(self.table_notas)
                    self.set_notas(bd.cadastrar_empresas(self.cnpj, self.nome))

        except OSError:
            pass

    def busca_notas(self):

        try:
            for item in range(self.notas.topLevelItemCount()):
                tree = self.notas.topLevelItem(item)
                self.chave = tree.text(0)
                self.nome_for = tree.text(2)
                check = tree.checkState(0).value

                if check == 2:
                    self.chave_nota = self.chave
                    self.stackedWidget.setCurrentWidget(self.table_itens)
                    self.table_center(
                        bd.seek_NotaFiscalID(
                            self.chave_nota
                        ))

        except OSError:
            pass

    def calculo_imposto(self):
        try:
            for item in range(self.itens.topLevelItemCount()):
                tree = self.itens.topLevelItem(item)
                NomeProduto = tree.text(0)
                valor_total = tree.text(7)
                aliquota_icms = tree.text(10)
                valor_icms = tree.text(11)
                valor_ipi = tree.text(12)
                valor_frete = tree.text(13)
                valor_outras = tree.text(14)
                valor_desconto = tree.text(15)
                check = tree.checkState(0).value

                if check == 2:
                    self.conn.execute(
                        "SELECT ID "
                        "FROM Itens WHERE NomeProduto = ? AND NotaFiscalID = ?",
                        (NomeProduto, bd.seek_NotaFiscalID(
                            self.chave_nota)))

                    item_id = self.conn.fetchone()

                    if item_id:
                        valor = calculo_diferencial_icms(
                            valor_total, aliquota_icms, valor_icms, valor_ipi,
                            valor_frete, valor_outras, valor_desconto)

                        sql = "UPDATE itens SET ValorImposto = ? WHERE id = ?"

                        self.conn.execute(sql, (str(valor), item_id[0]))
                        self.connec.commit()

        except OSError:
            pass

        self.table_center(bd.seek_NotaFiscalID(
            self.chave_nota))

    def zerar_imposto(self):
        try:
            for item in range(self.itens.topLevelItemCount()):
                tree = self.itens.topLevelItem(item)
                NomeProduto = tree.text(0)
                check = tree.checkState(0).value

                if check == 2:
                    self.conn.execute(
                        "SELECT ID "
                        "FROM Itens WHERE NomeProduto = ? AND NotaFiscalID = ?",
                        (NomeProduto, bd.seek_NotaFiscalID(
                            self.chave_nota
                        )))
                    item_id = self.conn.fetchone()

                    if item_id:
                        sql = "UPDATE itens SET ValorImposto = ? WHERE id = ?"
                        self.conn.execute(sql, (str(0), item_id[0]))
                        self.connec.commit()

        except OSError:
            pass

        self.table_center(bd.seek_NotaFiscalID(
            self.chave_nota))

    def select_all(self):
        for item in range(self.itens.topLevelItemCount()):
            try:
                tree = self.itens.topLevelItem(item)
                tree.setCheckState(0, Qt.CheckState.Checked)

            except ValueError:
                pass

    def mark_off_all(self):
        for item in range(self.itens.topLevelItemCount()):
            try:
                tree = self.itens.topLevelItem(item)
                tree.setCheckState(0, Qt.CheckState.Unchecked)

            except ValueError:
                pass

    def check_selection_pre(self):
        for item in range(self.itens.topLevelItemCount()):
            try:
                tree = self.itens.topLevelItem(item)
                check = tree.checkState(0).value

                if check == 1:
                    tree.setCheckState(0, Qt.CheckState.Checked)

            except ValueError:
                pass

        self.calculo_imposto()

    def somar_imposto(self):
        self.imposto = 0.0

        for item in range(self.itens.topLevelItemCount()):
            try:
                tree = self.itens.topLevelItem(item)
                self.NomeProduto = tree.text(0)
                self.conn = self.connec.cursor()
                self.conn.execute(
                    "SELECT ValorImposto "
                    "FROM Itens WHERE NomeProduto = ? AND NotaFiscalID = ?",
                    (self.NomeProduto, bd.seek_NotaFiscalID(
                        self.chave_nota)))
                valor = self.conn.fetchone()
                if valor:
                    self.imposto += float(valor[0])

            except ValueError:
                pass
            
        text_label = f'R$ {self.imposto}' 
        self.label_itens_imposto.setText(text_label)
        
        
    def emitir_dua(self):
        Dua().emitir_dua_sefaz(
            self.imposto, self.cnpj_dest, str(int(self.chave_nota[-19: -10])),
            self.nome_for, datetime.now())


if __name__ == '__main__':
    app = QApplication(argv)
    window = Ui()
    window.table_home()
    window.show()
    app.exec()
