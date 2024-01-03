import bd
from os import getlogin
from datetime import datetime, date, timedelta
from calendar import monthrange


def cadastrar_produto(
    cests, alis, ncms, name_prods, v_produtos, v_ipis, v_fretes, v_descs, v_outros,
    cnpj_des, nome_cli, chave_nf, data_e_hora, Valor_total, origs, csts, ucoms,
    qcoms, vuncoms, cfops, v_icms, name_for
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
                cnpj_des, nome_cli), chave_nf, data_e_hora, name_for, Valor_total,
                DataOperacao, getlogin()), name_prod, ncm, cest, cfop, ucom, 
                qcom, vuni, v_produto, orig, cst, ali, icms, float(v_ipi),
                v_frete, v_outro, v_desc, 0
                )
    return chave_nf
    
#Calcula o valor do imposto e o retorna
def calculo_diferencial_icms(
    valor_total, ali, valor_icms, valor_ipi, valor_frete, valor_outras, valor_desconto,
    aliquota_dif = 17.0, ativo_imo = False):
    base_de_calculo_ipi = ((
        float(valor_total) + float(valor_ipi) +
        float(valor_frete) + float(valor_outras) - float(valor_desconto)
        ) * (1 - (float(ali)/100))) / float(1-float(aliquota_dif/100)) * float(aliquota_dif/100)
    if ativo_imo == False:
        if float(valor_icms) == 0.0:
            v_impoto = base_de_calculo_ipi - (float(valor_total)+ float(valor_frete) 
                    + float(valor_outras) - float(valor_desconto)) * (float(ali)/100)
        else:
            v_impoto = base_de_calculo_ipi - float(valor_icms)
    else:
        if float(valor_icms) == 0.0:
            v_impoto = base_de_calculo_ipi - (float(valor_total)+ float(valor_frete) 
                    + float(valor_outras) + float(valor_ipi) - float(valor_desconto)
                    ) * (float(ali)/100)
        else:
            v_impoto = base_de_calculo_ipi - float(valor_icms) - (float(valor_ipi) * (float(ali)/100))
        
    return round(v_impoto, 2)

def date_last() -> str:
    """ Return the last day of the month, in str format.
        Always being the competence of the previous month.
        Example Month 06:
        Return 30/06/2023
    """
    data_atual = date.today()
    if data_atual.month == 1:
        month = 12
        year = data_atual.year -1
    else:
        month = (data_atual.month - 1)
        year = data_atual.year 
    last_date = data_atual.replace(day=1, month=month) + timedelta(
        monthrange(data_atual.year, month)[1] - 1)
    return f'{last_date.day:02}/{last_date.month:02}/{year}'


def date_start() -> str:
    """Return the start day of the month, in str format.
        Always being the competence of the previous month.
        Example Month 06:
        Return 01/06/2023
    """
    data_atual = date.today()
    
    if data_atual.month == 1:
        month = 12
        year = data_atual.year -1
    else:
        month = (data_atual.month - 1)
        year = data_atual.year 
    start_date = data_atual.replace(day=1, month=month, year=year)
    return f'{start_date.day:02}/{start_date.month:02}/{start_date.year}'