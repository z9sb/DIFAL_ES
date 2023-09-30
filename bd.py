import sqlite3
from os import path

# Conectar-se ao banco de dados (ou criar um novo se não existir)
conn = sqlite3.connect('dados.db')
cursor = conn.cursor()

try:
    if not path.exists('dados.bd'):
        cursor.execute('''CREATE TABLE Empresas (
                        ID INTEGER PRIMARY KEY,
                        CNPJ TEXT,
                        Nome TEXT
                    )''')

        # Criar tabela de notas fiscais
        cursor.execute('''CREATE TABLE NotasFiscais (
                            ID INTEGER PRIMARY KEY,
                            EmpresaID INTEGER,
                            Chave TEXT,
                            DataEmissao DATE,
                            NomeFornecedor TEXT,
                            ValorTotal DECIMAL,
                            DataOperacao DATE,
                            Usuario TEXT,
                            FOREIGN KEY (EmpresaID) REFERENCES Empresas(ID)
                        )''')

        # Criar tabela de itens de notas fiscais
        cursor.execute('''CREATE TABLE Itens (
                            ID INTEGER PRIMARY KEY,
                            NotaFiscalID INTEGER,
                            NomeProduto TEXT,
                            NCM TEXT,
                            CEST TEXT,
                            CFOP TEXT,
                            UCOM TEXT,
                            QCOM TEXT,
                            VUNCOM TEXT,
                            VPROD DECIMAL,
                            ICMSORIG TEXT,
                            ICMSCST TEXT,
                            AliICMS DECIMAL,
                            ValorICMS DECIMAL,
                            ValorIPI DECIMAL,
                            ValorFrete DECIMAL,
                            ValorOutras DECIMAL,
                            ValorDesconto DECIMAL,
                            ValorImposto DECIMAL,
                            FOREIGN KEY (NotaFiscalID) REFERENCES NotasFiscais(ID)
                        )''')

except:
    pass

def cadastrar_empresas(cnpj, nome):
    cursor.execute("SELECT ID FROM Empresas WHERE CNPJ = ?", (cnpj,))
    empresa_id = cursor.fetchone()
    
    if empresa_id:
        return empresa_id[0]
    else:
        cursor.execute("INSERT INTO Empresas (CNPJ, Nome) VALUES(?, ?)", (cnpj, nome))
        return cursor.lastrowid


def cadastrar_nota(
    EmpresaID, Chave, DataEmissao, NomeForncedor, ValorTotal, DataOperacao, Usuario):
    cursor.execute("SELECT ID FROM NotasFiscais WHERE Chave = ?", (Chave,))
    chave_id = cursor.fetchone()
    
    if chave_id:
        return chave_id[0]
    else:
        cursor.execute(
            "INSERT INTO NotasFiscais "
            "(EmpresaID, Chave, DataEmissao, NomeFornecedor, ValorTotal, DataOperacao,"
            "Usuario) VALUES(?, ?, ?, ?, ?, ?, ?)", 
            (EmpresaID, Chave, DataEmissao, NomeForncedor,
             ValorTotal, DataOperacao, Usuario))
        return cursor.lastrowid


def cadastrar_itens(NotaFiscalID, NomeProduto, NCM, CEST, CFOP, UCOM, QCOM, VUNCOM,
                    VPROD, ICMSORIG, ICMSCST, AliICMS, ValorICMS,ValorIPI, ValorFrete,
                    ValorOutras, ValorDesconto, ValorImposto):
    
    cursor.execute("SELECT ID FROM Itens WHERE NomeProduto = ? AND NotaFiscalID = ?", 
                   (NomeProduto, NotaFiscalID))
    item_id = cursor.fetchone()
    
    if item_id:
        return item_id[0]
    
    else:
        cursor.execute(
            "INSERT INTO Itens (NotaFiscalID, NomeProduto, NCM, CEST, CFOP, UCOM, QCOM,"
            "VUNCOM, VPROD, ICMSORIG, ICMSCST, AliICMS, ValorICMS, ValorIPI,ValorFrete,"
            "ValorOutras, ValorDesconto, ValorImposto) "
            "VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (NotaFiscalID, NomeProduto, NCM, CEST, CFOP, UCOM, QCOM, VUNCOM, VPROD,
            ICMSORIG, ICMSCST, AliICMS, ValorICMS, ValorIPI, ValorFrete, ValorOutras,
            ValorDesconto, ValorImposto)
        )
    
    return conn.commit()


def seek_id_nf_item(NotaFiscalID):
    cursor.execute(
        "SELECT NomeProduto, NCM, CEST, CFOP, UCOM, QCOM, VUNCOM, VPROD, ICMSORIG,"
        "ICMSCST, AliICMS, ValorICMS, ValorIPI, ValorFrete, ValorOutras, ValorDesconto,"
        "ValorImposto FROM Itens WHERE NotaFiscalID = ?", (NotaFiscalID,))
    item_id = cursor.fetchall()
    
    if item_id:
        return item_id
    
    
def seek_NotaFiscalID(Chave: str):
    cursor.execute("SELECT ID FROM NotasFiscais WHERE Chave = ?", (Chave,))
    chave_id = cursor.fetchone()
    return chave_id[0]


def notas_empresa(cnpj, nome):
    cursor.execute("SELECT ID FROM NotasFiscais WHERE EmpresaID = ?",
                   (cadastrar_empresas(cnpj, nome),))
    item_id = cursor.fetchall()
    
    if item_id:
        return item_id