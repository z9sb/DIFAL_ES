from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import time, sleep

class Dua:
    def send_delayed_keys(self, element, text, delay=0.3):
            for c in text:
                endtime = time() + delay
                element.send_keys(c)
                sleep(endtime - time())

    def emitir_dua_sefaz(self, imposto, cnpj, n_nf, n_for, data_e_hora):
            month = data_e_hora.month + 2

            if month > 12:
                  month = data_e_hora.month -12
            else:
                  month = data_e_hora.month +2

            if month >= 12:
                  year = data_e_hora.year + 1
            else:
                  year = data_e_hora.year
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            nav = webdriver.Chrome(options= chrome_options)
            
            nav.get("https://internet.sefaz.es.gov.br/agenciavirtual/area_publica/e-dua/icms.php")
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[2]/td[2]/select").click()
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[2]/td[2]/select/option[6]").click()
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[3]/td[2]/input").click()
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[3]/td[2]/input").send_keys(
                                    f"{data_e_hora.month:02}/{data_e_hora.year}"
                                )
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[5]/td[2]/input").click()
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[5]/td[2]/input").send_keys(
                                    f"{imposto:.2f}"
                                )
            g = nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[1]/td[2]/input")
            
            self.send_delayed_keys(g,cnpj, 0.3)
            
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[7]/td[2]/input").send_keys(
                                    f"REF. NF N°{n_nf} {str(n_for)}"
                                )
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[4]/td[2]/input").click()
            nav.find_element(
                                By.XPATH ,"/html/body/div[3]/div[2]/div[2]/fieldset/form/table/tbody/tr[4]/td[2]/input").send_keys(
                                    f"10/{month :02}/{year}")
            
            return None