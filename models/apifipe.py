# -*- coding: utf-8 -*-
import requests
import logging

_logger = logging.getLogger(__name__)

class FipeApiError(Exception):
    """Custom exception for FIPE API related errors."""
    pass

class apiFIPE:
    """
    A class to interact with the FIPE vehicle API, optimized for performance and usability.
    """
    BASE_URL = "https://veiculos.fipe.org.br/api/veiculos"

    def __init__(self, tipo_veiculo=1):
        """
        Initializes the FIPE API client.
        :param tipo_veiculo: 1 for Cars, 2 for Motorcycles, 3 for Trucks.
        """
        self.tipo_veiculo = tipo_veiculo
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Host": "veiculos.fipe.org.br",
            "Origin": "https://veiculos.fipe.org.br",
            "Referer": "https://veiculos.fipe.org.br/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        })
        
        self.codigo_tabela_referencia = self._get_codigo_tabela_referencia()

    def _get_codigo_tabela_referencia(self):
        """Fetches the latest reference table code. Internal method."""
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarTabelaDeReferencia")
            response.raise_for_status()
            return response.json()[0]["Codigo"]
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Error fetching reference table: {e}")
        except (KeyError, IndexError):
             raise FipeApiError("Could not parse reference table response. API may have changed.")


    def get_valor_por_codigo_fipe(self, ano_modelo, codigo_fipe):
        """
        Fetches vehicle value using only the FIPE code and year.
        This method hardcodes the fuel type to 5 (Flex Fuel) as requested.
        """
        if not self.codigo_tabela_referencia:
            raise FipeApiError("Reference table code is not available.")

        data = {
            "codigoTabelaReferencia": self.codigo_tabela_referencia,
            "codigoMarca": "",
            "codigoModelo": "",
            "codigoTipoVeiculo": self.tipo_veiculo,
            "anoModelo": int(ano_modelo),
            "codigoTipoCombustivel": 5,  # Hardcoded to 5 for Flex Fuel
            "tipoVeiculo": "carro",
            "modeloCodigoExterno": codigo_fipe,
            "tipoConsulta": "codigo",
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarValorComTodosParametros", data=data)
            response.raise_for_status()
            json_response = response.json()
            
            # The API can return an error message in a valid JSON response
            if 'erro' in json_response or 'codigo' in json_response and json_response.get('Valor') is None:
                error_msg = json_response.get('erro', 'Unknown API Error')
                if not error_msg and 'codigo' in json_response:
                     error_msg = f"API returned error code: {json_response['codigo']}"
                _logger.warning("FIPE API returned an error for FIPE code %s: %s", codigo_fipe, error_msg)
                raise FipeApiError(error_msg)
                
            return json_response
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Network error fetching vehicle value by FIPE code: {e}")
        except ValueError: # Catches JSON decoding errors
            raise FipeApiError("Failed to decode API response. The API might be down or has changed.")