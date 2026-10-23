# mapper.py
# FASE MAP: emite (nome_coluna, (x, y, x2, y2, xy, n)) para cada par (temp, valor).
# O Mapper NAO calcula correlacao. Ele so organiza os dados e conta o que rejeitou.
from collections import Counter


class Mapper:
    COLUMNS = ["X", "Y", "month", "day", "FFMC", "DMC",
               "DC", "ISI", "temp", "RH", "wind", "rain", "area"]

    TEMP_INDEX = 8  # coluna 9 (base 1) = indice 8 (base 0)

    NUMERIC_INDICES = {
        0: "X", 1: "Y", 4: "FFMC", 5: "DMC", 6: "DC",
        7: "ISI", 9: "RH", 10: "wind", 11: "rain", 12: "area",
    }

    def __init__(self):
        # Equivalente aos Counters do Hadoop: nada some sem deixar rastro
        self.counters = Counter()

    def map(self, lines: list) -> list:
        """Recebe um split (lista de linhas) e emite pares (chave, valor composto)."""
        emitted = []

        for line in lines:
            line = line.strip()

            if not line:
                self.counters["linhas_vazias"] += 1
                continue

            row = [c.strip() for c in line.split(",")]

            if row[0] == "X":  # cabecalho
                self.counters["cabecalho"] += 1
                continue

            self.counters["linhas_lidas"] += 1

            if len(row) != len(self.COLUMNS):
                self.counters["linhas_rejeitadas"] += 1
                continue

            try:
                x = float(row[self.TEMP_INDEX])  # temperatura
            except ValueError:
                self.counters["linhas_rejeitadas"] += 1
                continue

            self.counters["registros_validos"] += 1

            for idx, col_name in self.NUMERIC_INDICES.items():
                try:
                    y = float(row[idx])
                except ValueError:
                    self.counters[f"valor_invalido_{col_name}"] += 1
                    continue

                # Valor composto: ja no formato que Combiner e Reducer somam.
                # (x, y, x^2, y^2, x*y, n) -> o par (x, y) da MESMA linha nunca e separado
                emitted.append((col_name, (x, y, x * x, y * y, x * y, 1)))

        return emitted