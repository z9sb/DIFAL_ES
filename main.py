from os import path, walk
from pathlib import Path
from easygui import diropenbox #type: ignore 
from funcoes import cadastrar_produto
from xml_file import NFe
from datetime import datetime

if not path.exists('dir.txt'):
    rootdir = diropenbox(default= 'C:\donwload\*.xml')
        
    with open('dir.txt', 'w') as item:
        item.write(rootdir)
    root_dir = Path(rootdir)
else:
    with open('dir.txt') as item:
        root_dir = Path(item.read())
    
file_xml = []
for pasta_atual, subpastas, arquivos in walk(root_dir):
    for arquivo in arquivos: 
        if arquivo.endswith('.xml'): 
            file_xml.append(path.join(pasta_atual, arquivo))

list_cnpj: list = ['39389523000107', '30546485000184', '04118332000126']

def main(file_xml):
    print(file_xml)
    for root_file in file_xml:
        try:    
            xml = NFe(root_file)
            cnpj_des = xml.cnpj_dest()
            estado_cli = xml.estado_cli()
            estado_for = xml.estado_for()
            
            if estado_cli == estado_for or not cnpj_des in list_cnpj:
                pass

            else:
                cests = xml.cest()
                alis = xml.ali_icms()
                ncms = xml.ncm()
                name_prods = xml.name_prod()
                v_ipis = xml.v_ipi()
                v_produtos = xml.v_prod()
                v_fretes = xml.v_frete()
                v_descs = xml.v_desc()
                v_outros = xml.v_outros()
                n_nf = xml.number_nf()
                chave_nf = xml.acess_key()
                name_for = xml.name_for()
                nome_cli = xml.name_cli()
                origs = xml.icms_orig()
                cfops = xml.cfop()
                csts = xml.icms_cst()
                ucoms = xml.u_com()
                qcoms = xml.q_com()
                vuncoms = xml.v_uncom()
                v_icms = xml.v_icms()
                data_e_hora_em_texto = xml.date_emition()
                data_e_hora = datetime.strptime(data_e_hora_em_texto, '%Y-%m-%dT%H:%M:%S%z')
                Valor_total = xml.Valor_total()
                
                resultado = cadastrar_produto(
                    cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, 
                    v_outros, cnpj_des, nome_cli, chave_nf, data_e_hora, Valor_total, origs,
                    csts, ucoms, qcoms, vuncoms, cfops, v_icms, name_for)
                
                print(resultado)
        except:
            pass

if __name__ == '__main__':
    main(file_xml)