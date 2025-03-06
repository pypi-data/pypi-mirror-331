import requests
from typing import Dict
from src.services.cep_interface import CepServiceInterface


class ViaCepService(CepServiceInterface):

    def buscar_cep(self, cep: str) -> Dict:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Erro ao buscar o CEP: {response.status_code}")

        data = response.json()

        if "erro" in data:
            raise ValueError("CEP não encontrado.")

        return data
