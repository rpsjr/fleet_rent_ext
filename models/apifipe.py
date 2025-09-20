# -*- coding: utf-8 -*-
import requests

# 4. Custom Exception for cleaner error handling
class FipeApiError(Exception):
    """Custom exception for FIPE API related errors."""
    pass

class apiFIPE:
    """
    A class to interact with the FIPE vehicle API, optimized for performance and usability.
    """
    BASE_URL = "https://veiculos.fipe.org.br/api/veiculos"

    # 3. Vehicle type is set on initialization for consistency
    # def __init__(self, tipo_veiculo=1):
    def __init__(self):
        """
        Initializes the FIPE API client.
        :param tipo_veiculo: 1 for Cars, 2 for Motorcycles, 3 for Trucks.
        """
        #self.tipo_veiculo = tipo_veiculo
        self.tipo_veiculo = 1
        # 1. Use a single Session object for all requests
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Host": "veiculos.fipe.org.br",
            "Origin": "https://veiculos.fipe.org.br",
            "Referer": "https://veiculos.fipe.org.br/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        })

        # 2. Caching dictionaries to store results and avoid redundant API calls
        self._marcas_cache = None
        self._modelos_cache = {}
        
        self.codigo_tabela_referencia = self._get_codigo_tabela_referencia()

    def _get_codigo_tabela_referencia(self):
        """Fetches the latest reference table code. Internal method."""
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarTabelaDeReferencia")
            response.raise_for_status()
            return response.json()[0]["Codigo"]
        except requests.exceptions.RequestException as e:
            # Raise our custom exception
            raise FipeApiError(f"Error fetching reference table: {e}")

    def get_marcas(self):
        """Fetches all brands, using a cache to avoid repeated calls."""
        # 2. Check cache first
        if self._marcas_cache is not None:
            return self._marcas_cache

        data = {
            "codigoTabelaReferencia": self.codigo_tabela_referencia,
            "codigoTipoVeiculo": self.tipo_veiculo,
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarMarcas", data=data)
            response.raise_for_status()
            self._marcas_cache = response.json() # Store result in cache
            return self._marcas_cache
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Error fetching brands: {e}")

    def get_cod_marca(self, str_marca):
        """Finds the brand code for a given brand name."""
        marcas = self.get_marcas()
        for marca in marcas:
            if marca["Label"].lower() == str_marca.lower():
                return marca
        raise FipeApiError(f"Brand not found: '{str_marca}'")

    def get_modelos(self, codigo_marca):
        """Fetches all models for a given brand, using a cache."""
        # 2. Check cache for this specific brand code
        if codigo_marca in self._modelos_cache:
            return self._modelos_cache[codigo_marca]

        data = {
            "codigoTabelaReferencia": self.codigo_tabela_referencia,
            "codigoTipoVeiculo": self.tipo_veiculo,
            "codigoMarca": codigo_marca,
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarModelos", data=data)
            response.raise_for_status()
            modelos = response.json().get("Modelos", [])
            self._modelos_cache[codigo_marca] = modelos # Store result in cache
            return modelos
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Error fetching models for brand code {codigo_marca}: {e}")

    def get_anos_modelo(self, codigo_marca, codigo_modelo):
        """Fetches all model years for a given brand and model."""
        data = {
            "codigoTabelaReferencia": self.codigo_tabela_referencia,
            "codigoTipoVeiculo": self.tipo_veiculo,
            "codigoMarca": codigo_marca,
            "codigoModelo": codigo_modelo,
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarAnoModelo", data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Error fetching model years for model {codigo_modelo}: {e}")

    def get_valor_veiculo(self, codigo_marca, codigo_modelo, ano_modelo_combustivel):
        """Fetches the vehicle's value."""
        try:
            ano, cod_combustivel = ano_modelo_combustivel.split('-')
        except ValueError:
            raise FipeApiError(f"Invalid format for ano_modelo_combustivel: '{ano_modelo_combustivel}'")

        data = {
            "codigoTabelaReferencia": self.codigo_tabela_referencia,
            "codigoMarca": codigo_marca,
            "codigoModelo": codigo_modelo,
            "codigoTipoVeiculo": self.tipo_veiculo,
            "anoModelo": int(ano),
            "codigoTipoCombustivel": int(cod_combustivel),
            "tipoConsulta": "tradicional",
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/ConsultarValorComTodosParametros", data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FipeApiError(f"Error fetching vehicle value: {e}")


if __name__ == "__main__":
    try:
        # Initialize the API for Cars (tipo_veiculo=1)
        fipe_api_carros = apiFIPE(tipo_veiculo=1)
        print("--- Querying for Cars ---")

        # 1. Get brand info
        marca_info = fipe_api_carros.get_cod_marca("Fiat")
        print(f"Brand Info: {marca_info}")
        codigo_marca_fiat = marca_info['Value']

        # 2. Get models
        modelos_fiat = fipe_api_carros.get_modelos(codigo_marca_fiat)
        if not modelos_fiat:
            raise FipeApiError("No models found for Fiat.")
        
        primeiro_modelo = modelos_fiat[0]
        codigo_modelo_exemplo = primeiro_modelo['Value']
        print(f"\nUsing model '{primeiro_modelo['Label']}' (Code: {codigo_modelo_exemplo}) for demonstration...")

        # 3. Get model years
        anos_modelo = fipe_api_carros.get_anos_modelo(codigo_marca_fiat, codigo_modelo_exemplo)
        if not anos_modelo:
            raise FipeApiError("No model years found for the selected model.")
        
        print(f"\nAvailable Model Years: {anos_modelo}")
        ano_combustivel = anos_modelo[0]['Value']

        # 4. Get final value
        valor_veiculo = fipe_api_carros.get_valor_veiculo(codigo_marca_fiat, codigo_modelo_exemplo, ano_combustivel)
        print(f"\nVehicle Value: {valor_veiculo}")

    except FipeApiError as e:
        print(f"\nAn error occurred: {e}")