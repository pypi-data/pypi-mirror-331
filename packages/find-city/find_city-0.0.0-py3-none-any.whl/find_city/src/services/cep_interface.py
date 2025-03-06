from abc import ABC, abstractmethod
from typing import Dict


class CepServiceInterface(ABC):

    @abstractmethod
    def buscar_cep(self, cep: str) -> Dict:
        """Busca informações de um CEP"""
        pass
