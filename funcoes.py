import bd
from os import getlogin
from datetime import datetime

def cadastrar_produto(
    cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, v_outros,
    cnpj_des, nome_cli, chave_nf, data_e_hora, Valor_total, origs, csts, ucoms,
    qcoms, vuncoms, cfops, v_icms
):
    DataOperacao = datetime.now()

    for (
        cest, ali, ncm, name_prod, v_produto, v_ipi,
        v_frete, v_desc, v_outro, cfop, ucom, qcom, 
        vuni, orig, cst, icms
        )  in zip(
        cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, v_outros,
        cfops, ucoms, qcoms, vuncoms, origs, csts, v_icms):
            
            bd.cadastrar_itens(
                bd.cadastrar_nota(bd.cadastrar_empresas(
                cnpj_des, nome_cli), chave_nf, data_e_hora, Valor_total, DataOperacao,
                getlogin()), name_prod, ncm, cest, cfop, ucom, qcom, vuni, v_produto,
                orig, cst, ali, icms, float(v_ipi), v_frete, v_outro, v_desc,
                0, 0, 0
                )
    return chave_nf
    
#Calcula o valor do imposto e o retorna
def calculo_diferencial_icms(
    cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, v_outros,
    cnpj_des, nome_cli, chave_nf, data_e_hora, Valor_total, origs, csts, ucoms,
    qcoms, vuncoms, cfops, v_icms
    ):
    
    DataOperacao = datetime.now()
    
    v_impoto = 0
    for (
        cest, ali, ncm, name_prod, v_produto, v_ipi,
        v_frete, v_desc, v_outro, cfop, ucom, qcom, 
        vuni, orig, cst, icms
        )  in zip(
        cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, v_outros,
        cfops, ucoms, qcoms, vuncoms, origs, csts, v_icms):
        
            base_de_calculo_ipi = ((
                float(v_produto) + float(v_ipi) +
                float(v_frete) + float(v_outro) - float(v_desc)
                ) * (1 - (float(ali)/100))) * 0.83 * 0.17
            
            base_desconto_icms = (
                float(v_produto) - float(v_desc)) * (float(ali)/100)
            
            v_impoto += base_de_calculo_ipi - base_desconto_icms
            
            bd.cadastrar_itens(
                bd.cadastrar_nota(bd.cadastrar_empresas(
                cnpj_des, nome_cli), chave_nf, data_e_hora, Valor_total, DataOperacao,
                getlogin()), name_prod, ncm, cest, cfop, ucom, qcom, vuni, v_produto,
                orig, cst, ali, icms, float(v_ipi), v_frete, v_outro, v_desc,
                base_de_calculo_ipi, base_desconto_icms, 
                (base_de_calculo_ipi-base_desconto_icms)
            )
    return v_impoto

