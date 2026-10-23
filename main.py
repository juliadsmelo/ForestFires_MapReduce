# main.py - Orquestrador do pipeline MapReduce com Combiner
# Uso: python main.py
# Requisitos: pip install pandas scipy
import math
import zlib
from collections import Counter, defaultdict

import pandas as pd
from scipy import stats

from mapper import Mapper
from combiner import Combiner
from reducer import Reducer


class Main:
    FILEPATH = "forestfireinput.csv"
    NUM_NODES = 3       # simula 3 slaves
    NUM_REDUCERS = 2    # simula 2 reducers para mostrar o particionamento por chave
    COLUMNS = ["X", "Y", "month", "day", "FFMC", "DMC",
               "DC", "ISI", "temp", "RH", "wind", "rain", "area"]

    def run(self):
        results, counters, has_header = self._run_mapreduce()

        header = 0 if has_header else None
        df = pd.read_csv(self.FILEPATH, header=header, names=self.COLUMNS)

        self._check_integrity(results, counters, df)
        self._verify_against_pandas(results, df)
        self._outlier_analysis(df)

    # ---------------------------------------------------------------- MapReduce
    def _run_mapreduce(self):
        # PASSO 1 - SPLIT: divide as linhas em N pedacos (simula blocos do HDFS)
        with open(self.FILEPATH, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        has_header = bool(all_lines) and all_lines[0].strip().startswith("X")

        split_size = math.ceil(len(all_lines) / self.NUM_NODES)
        splits = [all_lines[i * split_size:(i + 1) * split_size]
                  for i in range(self.NUM_NODES)]

        # Integridade 1: nenhuma linha pode se perder na divisao
        assert sum(len(s) for s in splits) == len(all_lines), "Split perdeu linhas!"

        # PASSOS 2 e 3 - MAP + COMBINE, local em cada no
        total_counters = Counter()
        combined_all = []
        combiner = Combiner()

        for i, split in enumerate(splits, start=1):
            mapper = Mapper()                       # um Mapper por no
            mapped = mapper.map(split)              # MAP
            combined = combiner.combine(mapped)     # COMBINE
            combined_all.extend(combined)
            total_counters.update(mapper.counters)
            print(f"No {i}: {len(split)} linhas | {len(mapped)} pares emitidos "
                  f"-> {len(combined)} apos Combiner")

        # PASSO 4 - SHUFFLE & SORT: particiona por hash da CHAVE.
        # crc32 e estavel (o hash() de str do Python muda a cada execucao).
        partitions = [defaultdict(list) for _ in range(self.NUM_REDUCERS)]
        for key, value in combined_all:
            p = zlib.crc32(key.encode("utf-8")) % self.NUM_REDUCERS
            partitions[p][key].append(value)

        # PASSO 5 - REDUCE: cada reducer processa so as chaves da sua particao
        reducer = Reducer()
        results = {}
        for p, part in enumerate(partitions):
            print(f"Reducer {p}: colunas {sorted(part.keys())}")
            results.update(reducer.reduce(part))

        return results, total_counters, has_header

    # ---------------------------------------------------------------- Integridade
    def _check_integrity(self, results, counters, df):
        print("\n=== Contadores (integridade) ===")
        for k, v in sorted(counters.items()):
            print(f"  {k}: {v}")

        # Integridade 2: todo registro valido do CSV passou pelo MapReduce
        assert counters["registros_validos"] == len(df), \
            f"MapReduce viu {counters['registros_validos']} registros, CSV tem {len(df)}"

        # Integridade 3: toda coluna recebeu exatamente todos os registros
        for col, res in results.items():
            assert res["n"] == len(df), f"Coluna {col}: n={res['n']} != {len(df)}"

        print(f"  OK: {len(df)} registros em todas as {len(results)} colunas.")

    def _verify_against_pandas(self, results, df):
        print("\n=== Verificacao: MapReduce x pandas x Spearman (temp vs coluna) ===")
        rows = []
        for col, res in results.items():
            mr = res["pearson_r"]
            pd_r = df["temp"].corr(df[col])                 # sem arredondar
            rho, _ = stats.spearmanr(df["temp"], df[col])   # fora do MapReduce
            diff = abs(mr - pd_r)

            # Se divergir, o programa PARA (nao so imprime)
            assert diff < 1e-9, f"{col}: MapReduce={mr} pandas={pd_r} diff={diff}"
            rows.append((col, mr, pd_r, rho, res["strength"]))

        rows.sort(key=lambda r: abs(r[1]), reverse=True)  # ordenado por forca
        print(f"  {'col':<5} {'MapReduce':>10} {'pandas':>10} {'Spearman':>10}  forca")
        for col, mr, pd_r, rho, strength in rows:
            print(f"  {col:<5} {mr:>+10.4f} {pd_r:>+10.4f} {rho:>+10.4f}  {strength}")
        print("  OK: MapReduce identico ao pandas (diferenca < 1e-9).")

    # ---------------------------------------------------------------- Outliers
    def _outlier_analysis(self, df):
        print("\n=== Outliers (metodo IQR) ===")
        for col in ["temp", "FFMC", "rain", "area"]:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            n_out = int((df[col] > upper).sum())
            print(f"  {col:<5} limite sup={upper:8.2f}  outliers={n_out:3d} "
                  f"({100 * n_out / len(df):.1f}%)  media={df[col].mean():.2f} "
                  f"mediana={df[col].median():.2f}")


if __name__ == "__main__":
    Main().run()