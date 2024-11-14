from typing import List, Callable

def notify(self, data: dict):
    for observer in self._observers:
        try:
            observer(data)
        except Exception as e:
            print(f"Ошибка в наблюдателе: {e}")


class Subject:
    def __init__(self):
        self._observers: List[Callable[[dict], None]] = []

    def attach(self, observer: Callable[[dict], None]):
        self._observers.append(observer)

    def detach(self, observer: Callable[[dict], None]):
        self._observers.remove(observer)

    def notify(self, data: dict):
        for observer in self._observers:
            observer(data)
