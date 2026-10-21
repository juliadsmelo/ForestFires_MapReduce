# ----------------------------------------------------------------
# CLASSE 1 — Mapper
# ----------------------------------------------------------------
import csv
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

class Mapper:

    #Lê cada linha do CSV e emite pares (chave, valor).
    # Chave = mês | Valor = temperatura daquele registro.


    def __init__(self, filepath: str):
        self.filepath = filepath

    def map(self) -> list[tuple[str, float]]:
        """Retorna lista de tuplas (mes, temp)."""
        pairs: list[tuple[str, float]] = []
        with open(self.filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
            # Colunas: X,Y,month,day,FFMC,DMC,DC,ISI,temp,RH,wind,rain,area
            # Índices: 0,1, 2 , 3 , 4 , 5 , 6, 7 , 8 , 9, 10 , 11, 12
                month = row[2].strip().lower()
                temp = float(row[8])
                pairs.append((month, temp))
        print(f"[Mapper] {len(pairs)} pares (mês, temp) emitidos.")
        return pairs