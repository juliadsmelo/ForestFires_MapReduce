from mapper import Mapper      # puxa a classe do mapper.py
from reducer import Reducer    # puxa a classe do reducer.py

import csv
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

# ----------------------------------------------------------------
# CLASSE 3 — Main (Orquestrador)
# ----------------------------------------------------------------
class Main:

    # Orquestra o pipeline MapReduce e executa a análise
    # aprofundada (correlações, outliers e hipóteses).

    FILEPATH = "forestfireinput.csv"
    COLUMNS = ["X","Y","month","day","FFMC","DMC","DC","ISI", "temp","RH","wind","rain","area"]
    MONTH_ORDER = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]

    def run(self):
        print("=" * 65)
        print(" FASE 1 — MapReduce: Temperatura Média por Mês")
        print("=" * 65)
        self._run_mapreduce()
        print("\n" + "=" * 65)
        print(" FASE 2 — Análise Aprofundada (Correlações e Outliers)")
        print("=" * 65)
        df = self._load_dataframe()
        self._correlation_analysis(df)
        self._outlier_analysis(df)
        self._hypothesis_and_conclusions(df)

    def _run_mapreduce(self):
        mapper = Mapper(self.FILEPATH)
        reducer = Reducer()
        pairs = mapper.map() # MAP
        results = reducer.reduce(pairs) # REDUCE

        print(f"\n{'Mês':<6} {'N':>5} {'Média':>7} {'Mediana':>8} "
              f"{'DP':>7} {'Mín':>6} {'Máx':>6}")
        print("-" * 50)
        for m in self.MONTH_ORDER:
            if m in results:
                r = results[m]
                print(f"{m:<6} {r['count']:>5} {r['mean']:>7.2f} "
                      f"{r['median']:>8.2f} {r['std']:>7.2f} "
                      f"{r['min']:>6.1f} {r['max']:>6.1f}")
                
        all_temps = [pair[1] for pair in Mapper(self.FILEPATH).map()]
        print(f"\n>>> Temperatura média GLOBAL: {np.mean(all_temps):.2f} °C")
        print(">>> ATENÇÃO: essa média global esconde variações enormes!")

    def _load_dataframe(self) -> pd.DataFrame:
        return pd.read_csv(self.FILEPATH, header=None, names=self.COLUMNS)


    def _correlation_analysis(self, df: pd.DataFrame):
        numeric_cols = ["X","Y","FFMC","DMC","DC","ISI",
                        "temp","RH","wind","rain","area"]

        print("\n--- CORRELAÇÃO DE PEARSON (com temp) ---")
        corr = df[numeric_cols].corr()
        temp_corr = corr["temp"].drop("temp").sort_values(
            key=abs, ascending=False)
        for col, val in temp_corr.items():
            strength = self._interpret_corr(val)
            print(f"  temp x {col:<6} = {val:>+.4f}  ({strength})")


        print("\n--- TOP 10 PARES (valor absoluto) ---")
        pairs_seen = set()
        ranked = []
        for c1 in numeric_cols:
            for c2 in numeric_cols:
                if c1 >= c2: continue
                if (c1,c2) not in pairs_seen:
                    pairs_seen.add((c1,c2))
                    ranked.append((c1, c2, corr.loc[c1, c2]))
        ranked.sort(key=lambda x: abs(x[2]), reverse=True)
        for c1, c2, val in ranked[:10]:
            print(f"  {c1:<6} x {c2:<6} = {val:>+.4f}")


        print("\n--- CORRELAÇÃO DE SPEARMAN (com temp) ---")
        for col in numeric_cols:
            if col == "temp": continue
            rho, pval = stats.spearmanr(df["temp"], df[col])
            sig = "***" if pval < 0.001 else ("**" if pval < 0.01 else
                  ("*" if pval < 0.05 else "ns"))
            print(f"  temp x {col:<6} = {rho:>+.4f}  (p={pval:.4f}) {sig}")


    def _outlier_analysis(self, df: pd.DataFrame):
        print("\n--- DETECÇÃO DE OUTLIERS (método IQR x 1.5) ---")
        numeric_cols = ["FFMC","DMC","DC","ISI","temp","RH","wind","rain","area"]
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            pct = len(outliers) / len(df) * 100
            print(f"  {col:<6}: {len(outliers):>3} outliers ({pct:.1f}%)")


        print("\n--- OUTLIERS DE temp POR Z-SCORE (|z| > 2) ---")
        z_temp = np.abs(stats.zscore(df["temp"]))
        outliers_z = df[z_temp > 2]
        print(f"  {len(outliers_z)} registros com |z| > 2 para temperatura")


    def _hypothesis_and_conclusions(self, df):
        print("\n" + "=" * 65)
        print("  FASE 3 — Hipóteses e Conclusões para a Defesa")
        print("=" * 65)
        print("Ver documento de estudo para argumentos completos.")


    @staticmethod
    def _interpret_corr(val: float) -> str:
        v = abs(val)
        if v >= 0.7:   return "forte"
        elif v >= 0.4: return "moderada"
        elif v >= 0.2: return "fraca"
        else:          return "muito fraca / desprezível"




# ================================================================
# PONTO DE ENTRADA
# ================================================================
if __name__ == "__main__":
    Main().run()




    

            

