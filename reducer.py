# reducer.py
# FASE REDUCE: soma as parciais recebidas e aplica Pearson com os totais globais.
import math


class Reducer:
    def reduce(self, partition: dict) -> dict:
        """partition = {chave: [tuplas de 6 somas]} (ja agrupado pelo Shuffle)."""
        results = {}

        for col_name in sorted(partition.keys()):
            totals = [0.0] * 6
            for partial in partition[col_name]:
                for i, v in enumerate(partial):
                    totals[i] += v

            sx, sy, sx2, sy2, sxy, n = totals
            n = int(n)

            # r = (N*Sxy - Sx*Sy) / sqrt((N*Sx2 - Sx^2) * (N*Sy2 - Sy^2))
            numerator = n * sxy - sx * sy
            denom_x = n * sx2 - sx ** 2
            denom_y = n * sy2 - sy ** 2

            if n < 2 or denom_x <= 0 or denom_y <= 0:
                r = float("nan")  # correlacao indefinida (variancia zero), nao e 0
            else:
                r = numerator / math.sqrt(denom_x * denom_y)

            results[col_name] = {
                "n": n,
                "pearson_r": r,
                "strength": self._interpret(r),
            }

        return results

    @staticmethod
    def _interpret(r: float) -> str:
        if math.isnan(r):
            return "INDEFINIDA"
        v = abs(r)
        if v >= 0.7:
            return "FORTE"
        if v >= 0.4:
            return "MODERADA"
        if v >= 0.2:
            return "FRACA"
        return "MUITO FRACA / DESPREZIVEL"