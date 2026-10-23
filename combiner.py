# combiner.py
# FASE COMBINE: "mini-reducer" local, roda no proprio no antes do Shuffle.
# Entrada e saida tem o MESMO formato (chave, tupla de 6 somas).
# Por isso o Combiner e opcional: se o Hadoop nao rodar, o Reducer funciona igual.


class Combiner:
    def combine(self, pairs: list) -> list:
        acc = {}

        for key, values in pairs:
            if key not in acc:
                acc[key] = [0.0] * 6
            for i, v in enumerate(values):
                acc[key][i] += v

        return [(key, tuple(sums)) for key, sums in acc.items()]