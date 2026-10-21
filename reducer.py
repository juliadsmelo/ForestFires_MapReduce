# ----------------------------------------------------------------
# CLASSE 2 — Reducer
# ----------------------------------------------------------------
import csv
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

class Reducer:
    # Recebe os pares agrupados por chave (mês) e calcula a temperatura média, mediana, desvio padrão e contagem.

    def reduce(self, mapped_pairs: list[tuple[str, float]]) -> dict:
        # Agrupar valores por chave
        groups: dict[str, list[float]] = defaultdict(list)
        for key, value in mapped_pairs:
            groups[key].append(value)
        
        results = {}
        for key in sorted(groups.keys()):
            temps = groups[key]
            results[key] = {
                "count": len(temps),
                "mean": round(np.mean(temps), 2),
                "median": round(np.median(temps), 2),
                "std": round(np.std(temps, ddof=1), 2) if len(temps) > 1 else
0.0,
                "min": round(min(temps), 2),
                "max": round(max(temps), 2),
            }
        print(f"[Reducer] {len(results)} chaves (meses) reduzidas.")
        return results