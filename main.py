from os import path, remove, listdir
from pathlib import Path
from easygui import diropenbox #type: ignore 
from funcoes import cadastrar_produto
from xml_file import NFe
from datetime import datetime

if path.exists('rootdir.txt'):
    remove('rootdir.txt')
    
if not path.exists('rootdir.txt'):
    rootdir = diropenbox(default= 'C:\donwload\*.xml')
    
    with open('rootdir.txt', 'w') as f:
        f.write(rootdir)
        
with open('rootdir.txt') as dir_name:
    root_dir = Path(dir_name.readline())
    file_xml = list(i for i in listdir(root_dir) if i.endswith('.xml'))
    print(root_dir)
    for root_file in file_xml:
        root = (f'{root_dir}/{root_file}')
        
        xml = NFe(root)
        cests = xml.cest()
        alis = xml.ali_icms()
        ncms = xml.ncm()
        name_prods = xml.name_prod()
        v_ipis = xml.v_ipi()
        v_produtos = xml.v_prod()
        v_fretes = xml.v_frete()
        v_descs = xml.v_desc()
        v_outros = xml.v_outros()
        cnpj_des = xml.cnpj_dest()
        n_nf = xml.number_nf()
        chave_nf = xml.acess_key()
        name_for = xml.name_for()
        nome_cli = xml.name_cli()
        estado_cli = xml.estado_cli()
        estado_for = xml.estado_for()
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


        if estado_cli == estado_for:
            pass

        else:
            resultado = cadastrar_produto(
                cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, 
                v_outros, cnpj_des, nome_cli, chave_nf, data_e_hora, Valor_total, origs,
                csts, ucoms, qcoms, vuncoms, cfops, v_icms, name_for)
            
            print(resultado)
            
    