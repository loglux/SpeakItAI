from abc import ABC, abstractmethod

class ITTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str, **kwargs) -> str:
        pass
