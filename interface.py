import sqlite3
from sys import argv

from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QMessageBox

from funcoes import calculo_diferencial_icms, date_start, date_last
from emitir_dua import Dua
import bd
from datetime import datetime
from cachetools import TTLCache
import hashlib

class Ui(QMainWindow):   
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('untitled.ui', self)
        self.init_ui()
        self.cache = TTLCache(maxsize=1000, ttl=3600)

    def init_ui(self):
        self.empresas.itemClicked.connect(self.busca_empresa)
        self.notas.itemClicked.connect(self.busca_notas)

        self.btn_empresas.clicked.connect(self.btn_table_empresas)
        self.btn_itens.clicked.connect(self.btn_table_itens)
        self.btn_notas.clicked.connect(self.btn_table_notas)
        self.btn_notas.clicked.connect(self.next_notas)
        self.btn_itens_salvar.clicked.connect(self.calculo_imposto)
        self.btn_itens_dua.clicked.connect(self.emitir_dua)
        self.btn_itens_mt.clicked.connect(self.select_all)
        self.btn_itens_dt.clicked.connect(self.mark_off_all)
        self.btn_itens_zt.clicked.connect(self.zerar_imposto)
        self.btn_itens_cps.clicked.connect(self.check_selection_pre)
        self.lineedit_notas.textChanged.connect(self.search_nota)
        self.dateEdit_inicial.setDate(self.set_date(date_start()))
        self.dateEdit_final.setDate(self.set_date(date_last()))
        self.dateEdit_inicial.dateChanged.connect(self.search_nota)
        self.dateEdit_final.dateChanged.connect(self.search_nota)

        self.itens.setHeaderLabels(
            ['PRODUTO', 'NCM', 'CEST', 'CFOP', 'UNIDADE', 'QUANTIDADE',
             'VALOR UNI. PRODUTO', 'VALOR TOTAL PRODUTO', 'ORIG', 'CST',
             'ALIQUOTA ICMS', 'VALOR ICMS', 'VALOR IPI', 'VALOR FRETE',
             'VALOR OUTRAS', 'VALOR DESCONTO', 'VALOR IMPOSTO'])

    def set_date(self, metodo):
        dia, mes, ano = map(int, str(metodo).split('/'))
        return QDate(ano, mes, dia)

    def table_home(self):
        self.empresas.clear()
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
    
    def gerar_hash_parametros(self, empresa, pesquisa, data_inicial, data_final):
        # Gere um hash dos parâmetros para ser usado como chave de cache
        hash_input = f"{empresa}-{pesquisa}-{data_inicial}-{data_final}"
        return hashlib.md5(hash_input.encode()).hexdigest()    

    def search_nota(self):
        pesquisa = self.lineedit_notas.text()
        dt_in_nf = self.dateEdit_inicial.date()
        dt_fn_nf = self.dateEdit_final.date()
        data_inicial = f'{dt_in_nf.year()}-{dt_in_nf.month():02}-{dt_in_nf.day():02}'
        data_final = f'{dt_fn_nf.year()}-{dt_fn_nf.month():02}-{dt_fn_nf.day():02}'
        parametros_busca = [bd.cadastrar_empresas(self.cnpj_dest, self.nome_dest)]
        chave_cache = self.gerar_hash_parametros(self.cnpj_dest, pesquisa, data_inicial, data_final)

        # Verificar se o resultado já está em cache
        if chave_cache in self.cache:
            result = self.cache[chave_cache]
        else:
            # Caso não esteja em cache, fazer a consulta ao banco de dados
            search = ("SELECT Chave, DataEmissao, NomeFornecedor "
                      "FROM NotasFiscais WHERE EmpresaID = ? ")

            if pesquisa:
                search += "AND (Chave LIKE ? OR NomeFornecedor LIKE ?)"
                parametros_busca.extend(['%' + pesquisa + '%', '%' + pesquisa + '%'])

            if data_inicial:
                search += " AND DATETIME(DataEmissao, '-03:00') >= ?"
                parametros_busca.append(data_inicial)

            if data_final:
                search += " AND DATETIME(DataEmissao, '-03:00') <= ?"
                parametros_busca.append(data_final)

            result = self.conn.execute(search, parametros_busca).fetchall()

            # Armazenar o resultado em cache
            self.cache[chave_cache] = result

        return self.set_notas(result)

    def set_notas(self, result_list):
        self.notas.clear()
        notas_calculadas = {}

        def create_tree_item(index, nota):
            tree_item = QTreeWidgetItem(self.notas if nota[0] != self.elemento else self.campo, index)
            for col_index, item in enumerate(nota):
                tree_item.setText(col_index, item)
            tree_item.setCheckState(0, Qt.CheckState.Unchecked)
            return tree_item

        # Crie uma lista de QTreeWidgetItems
        tree_items = [create_tree_item(index, nota) for index, nota in enumerate(result_list)]
        
        # Lógica de manipulação de dados
        for index, nota in enumerate(result_list):
            nf_id = bd.seek_NotaFiscalID(nota[0])

            
            if not self.lineedit_notas.hasFocus():
                check_result = self.conn.execute( 
                    "SELECT NomeProduto " 
                    "FROM Itens " 
                    "WHERE NotaFiscalID IN ({}) " 
                    "GROUP BY NomeProduto HAVING COUNT(NomeProduto) > 1 " 
                    "AND SUM(CASE WHEN ValorImposto > 0 THEN 1 ELSE 0 END) > 0 " 
                    "AND NomeProduto IN (SELECT NomeProduto " 
                    "FROM Itens WHERE NotaFiscalID = ? " 
                    "AND ValorImposto = 0 )".format(', '.join(['?'] * len(self.notas_empr_pro))), 
                    (tuple(self.notas_empr_pro) + (nf_id,)) 
                ).fetchall()

                if check_result:
                    notas_calculadas[nota[0]] = [item[0] for item in check_result]
                    
        # Atualize suas variáveis de lista com as informações calculadas
        self.list_notas_cal = list(notas_calculadas.keys())
        self.list_itens_cal = list(notas_calculadas.values())

        if notas_calculadas:
            self.show_dialog()

    def notas_abertas(self):
        for item in range(self.notas.topLevelItemCount()):
            try:
                tree = self.notas.topLevelItem(item)
                chave = tree.text(0)

                if chave in self.list_notas_cal:
                    self.list_notas_cal.remove(chave)
                    tree.setCheckState(0, Qt.CheckState.Checked)
                    self.busca_notas()
                    yield tree.setCheckState(0, Qt.CheckState.Unchecked)

            except (StopIteration, AttributeError):
                pass

        self.notas.expandAll()

    def table_center(self, NotaFiscalID):
        self.itens.clear()
        result_list = bd.seek_id_nf_item(NotaFiscalID)

        def create_tree_item(valor):
            tree_item = QTreeWidgetItem(self.itens)
            for col, item in enumerate(valor):
                tree_item.setText(col, str(item))
                
            if valor[0] == self.elemento:
                tree_item.parent().removeChild(tree_item)
                self.campo.addChild(tree_item)
            elif self.list_itens_cal != []:
                if valor[0] in self.list_itens_cal[0]:
                    tree_item.setCheckState(0, Qt.CheckState.PartiallyChecked)
                else:
                    tree_item.setCheckState(0, Qt.CheckState.Unchecked)
            else:
                tree_item.setCheckState(0, Qt.CheckState.Unchecked)

        list(map(create_tree_item, result_list))

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
                    self.nome_dest = self.nome
                    self.notas_empr_pro = [i[0] for i in bd.notas_empresa(self.cnpj_dest, self.nome)]
                    self.stackedWidget.setCurrentWidget(self.table_notas)
                    self.search_nota()
                
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
        for item in range(self.itens.topLevelItemCount()):
            if item is not None:
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
            if item is not None:
                tree = self.itens.topLevelItem(item)
                tree.setCheckState(0, Qt.CheckState.Checked)

    def mark_off_all(self):
        for item in range(self.itens.topLevelItemCount()):
            if item is not None:
                tree = self.itens.topLevelItem(item)
                tree.setCheckState(0, Qt.CheckState.Unchecked)

    def check_selection_pre(self):
        for item in range(self.itens.topLevelItemCount()):
            if item is not None:
                tree = self.itens.topLevelItem(item)
                check = tree.checkState(0).value

                if check == 1:
                    tree.setCheckState(0, Qt.CheckState.Checked)

        self.calculo_imposto()

    def somar_imposto(self):
        self.imposto = 0.0

        for item in range(self.itens.topLevelItemCount()):
            try:
                tree = self.itens.topLevelItem(item)
                self.NomeProduto = tree.text(0)

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

        text_label = f'R$ {round(self.imposto, 2)}'
        self.label_itens_imposto.setText(text_label)

    def show_dialog(self):
        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle(
            'Notificação'
        )
        self.msg_box.setText(
            'Foram encontradas notas em aberto, deseja calcular?'
        )
        self.msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        result = self.msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            return self.notas_abertas()

    def next_notas(self):
        try:
            return next(self.notas_abertas())
        except:
            pass

    def emitir_dua(self):
        Dua().emitir_dua_sefaz(
            round(self.imposto, 2), self.cnpj_dest, str(
                int(self.chave_nota[-19: -10])),
            self.nome_for, datetime.now())


if __name__ == '__main__':
    app = QApplication(argv)
    window = Ui()
    window.table_home()
    window.show()
    app.exec()
