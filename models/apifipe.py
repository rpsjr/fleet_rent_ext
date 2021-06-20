# -*- coding: utf-8 -*-
import requests
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from requests.structures import CaseInsensitiveDict

class apiFIPE():

    def getCodigoMarca(self, anoModelo, modeloCodigoExterno):

        response = requests.post(
            'https://veiculos.fipe.org.br/api/veiculos//ConsultarValorComTodosParametros',
            json={'codigoTabelaReferencia': self.codigoTabelaReferencia(),
                    'codigoMarca': '',
                    'codigoModelo': '',
                    'codigoTipoVeiculo': 1, #CARRO
                    'anoModelo': anoModelo,
                    'codigoTipoCombustivel': 1,
                    'tipoVeiculo': 'carro',
                    'modeloCodigoExterno': modeloCodigoExterno,
                    'tipoConsulta': 'codigo'
                    },
            headers={
                'Host': 'veiculos.fipe.org.br',
                'Referer': 'http://veiculos.fipe.org.br/'
            }
        )

        return response.json()


    def getModelos(self, anoModelo, modeloCodigoExterno):

        response = requests.post(
            'http://veiculos.fipe.org.br/api/veiculos/ConsultarModelosAtravesDoAno',
            json={
                  "codigoTabelaReferencia": self.codigoTabelaReferencia(),
                  "codigoTipoVeiculo": 1,  #CARRO
                  "codigoMarca": 26,
                  "ano": "2011-1",
                  "codigoTipoCombustivel": 1,
                  "anoModelo": 2011
                },
            headers={
                'Host': 'veiculos.fipe.org.br',
                'Referer': 'http://veiculos.fipe.org.br/'
            }
        )

        return response.json()

    def getMarcas(self):

        response = requests.post(
            'http://veiculos.fipe.org.br/api/veiculos/ConsultarMarcas',
            json={
                  "codigoTabelaReferencia": self.codigoTabelaReferencia(),
                  "codigoTipoVeiculo": 1,  #CARRO
                },
            headers={
                'Host': 'veiculos.fipe.org.br',
                'Referer': 'http://veiculos.fipe.org.br/'
            }
        )

        return response.json()

    def getCodMarca(self, str_marca):




        marca = next((x for x in self.getMarcas() if x['Label'].lower() == str_marca.lower()), ['Não localizada'])
        #marca = self.getMarcas()
        #set(k.lower() for k in )
        #codigo = CaseInsensitiveDict(theset)['Fiat']
        #codigo = theset#['Fiat']


        return marca

    def codigoTabelaReferencia(self, *args):
        fipe_first_table = date(1999,1,1)
        if not args:
            data_ref = date.today()
        else:
            data_ref = [0]
        relativedelta_obj = relativedelta(data_ref, fipe_first_table)
        codTabela = relativedelta_obj.months + (12*relativedelta_obj.years)
        #if date.today().day <= 15:
        #    codTabela += 2
        #todo
        # confirmar se houve um salto na numeracao da tabela ou se adota-se uma
        #numeração temporária até o encerramento do mês
        if data_ref > date(2021,4,30):
             codTabela += 2
        #print('codTabela ' + str(codTabela))
        return codTabela


if __name__ == '__main__':
    #apiFIPE = apiFIPE()
    result = apiFIPE().getCodigoMarca(2018,'001461-3')
    print(result)
    result = apiFIPE().getCodMarca('GM - chevrolet')
    print(result)

    #strr ="{'Valor': 'R$ 34.196,00', 'Marca': 'Fiat', 'Modelo': 'MOBI LIKE 1.0 Fire Flex 5p.', 'AnoModelo': 2018, 'Combustivel': 'Gasolina', 'CodigoFipe': '001461-3', 'MesReferencia': 'março de 2021 ', 'Autenticacao': 'q78mr8l18q5h', 'TipoVeiculo': 1, 'SiglaCombustivel': 'G', 'DataConsulta': 'domingo, 28 de março de 2021 18:31'}"
    #print (strr)
