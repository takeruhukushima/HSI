import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
from datetime import datetime
import math

# --- Volcanoクラス (表示の明示化とTop 10ラベル対応) ---
class Volcano():
    def __init__(self, protein_id, ratio, pval, pcutoff, min_log2ratio, max_log2ratio):
        self.df = pd.DataFrame({'ID': protein_id, 'Ratio': ratio, '-log10(p-value)': pval})
        self.pcutoff = pcutoff
        self.min_log2 = min_log2ratio
        self.max_log2 = max_log2ratio
        
    def get_volcano(self, target_name, control_name, save_path, top_n=10):
        X = self.df['Ratio'].values
        y = self.df['-log10(p-value)'].values

        # 描画範囲の計算
        X_finite = X[np.isfinite(X)]
        y_finite = y[np.isfinite(y)]
        x_min = min(X_finite.min(), self.min_log2) - 1 if len(X_finite) > 0 else -4
        x_max = max(X_finite.max(), self.max_log2) + 1 if len(X_finite) > 0 else 8
        y_max = y_finite.max() + 1 if len(y_finite) > 0 else 5

        p_cutoff_val = -1 * math.log(self.pcutoff, 10)
        
        # 有意なプロテインの抽出とTop Nの選定
        df_sig = self.df[(self.df['-log10(p-value)'] > p_cutoff_val) & 
                         ((self.df['Ratio'] >= self.max_log2) | (self.df['Ratio'] <= self.min_log2))].copy()
        df_top = df_sig.sort_values('-log10(p-value)', ascending=False).head(top_n)

        # 描画設定
        sns.set()
        sns.set_context('talk')
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(14, 11))
        
        # 軸ラベルとタイトルを明示化
        xlabel_str = f"Log2 ({target_name} / {control_name})"
        title_str = f"Volcano Plot: {target_name} vs {control_name}\n(n=3, Control={control_name})"
        ax.set(xlabel=xlabel_str, ylabel='-Log10 (p-value)', title=title_str, 
               xlim=(x_min, x_max), ylim=(0, y_max))
        
        # 全体
        ax.scatter(X, y, s=50, color='gray', alpha=0.3, edgecolors='none')

        # 増加 (Targetで高い)
        df_inc = self.df[(self.df['Ratio'] >= self.max_log2) & (self.df['-log10(p-value)'] > p_cutoff_val)]
        ax.scatter(df_inc['Ratio'], df_inc['-log10(p-value)'], s=60, color='red', edgecolors='none', label=f'Up in {target_name}')
        
        # 減少 (Targetで低い)
        df_dec = self.df[(self.df['Ratio'] <= self.min_log2) & (self.df['-log10(p-value)'] > p_cutoff_val)]
        ax.scatter(df_dec['Ratio'], df_dec['-log10(p-value)'], s=60, color='blue', edgecolors='none', label=f'Down in {target_name}')

        # 閾値線
        ax.axvline(x=self.min_log2, color='black', linewidth=1.0, linestyle='--')
        ax.axvline(x=self.max_log2, color='black', linewidth=1.0, linestyle='--')
        ax.axhline(y=p_cutoff_val, color='black', linewidth=1.0, linestyle='--')
        
        # p=0.05 ラベル
        ax.text(x_max - 0.2, p_cutoff_val + 0.1, f'p = {self.pcutoff}', size=16, fontstyle="italic", ha='right')

        # Top 10 アノテーション
        for _, row in df_top.iterrows():
            py = row['-log10(p-value)'] if np.isfinite(row['-log10(p-value)']) else y_max - 0.3
            ax.annotate(str(row['ID']), (row['Ratio'], py),
                        xytext=(5, 5), textcoords='offset points', size=11, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='gray'))

        plt.legend(loc='upper right', fontsize=12)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

# --- メインロジック ---
def run_volcano_analysis(file_path, groups, comparisons, p_cutoff=0.05, min_log2=-1.0, max_log2=1.0, output_base_dir=None, sheet_name=0):
    """
    プロテオミクスデータのVolcano Plotを作成し、有意差解析を行います。
    
    Args:
        file_path: 解析対象のExcelファイルの絶対パス。
        groups: 群の名前とサンプリカラム名のマッピング。
        comparisons: 比較対象のペアのリスト [[target, control], ...]。
        p_cutoff: p値の閾値。
        min_log2: Log2FCの減少側の閾値。
        max_log2: Log2FCの増加側の閾値。
        output_base_dir: 結果の保存先ベースディレクトリ（絶対パス推奨）。
        sheet_name: 読み込むExcelシート名またはインデックス（デフォルト: 0）。
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    # 出力先ディレクトリの決定
    if output_base_dir is None:
        output_base_dir = os.path.join(os.getcwd(), "output_plot")
    else:
        output_base_dir = os.path.abspath(output_base_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Reading {file_path} (sheet: {sheet_name})...")
    print(f"Output will be saved to: {output_dir}")
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Protein.Names カラムを使用
    label_col = 'Protein.Names' if 'Protein.Names' in df_raw.columns else df_raw.columns[0]
    print(f"Using '{label_col}' for annotations.")

    for target, control in comparisons:
        print(f"Analyzing: {target} vs {control} (Control)...")
        if target not in groups or control not in groups:
            print(f"  Error: Group {target} or {control} not found in GROUPS.")
            continue

        cols_ctrl, cols_trgt = groups[control], groups[target]
        
        # 必要な列を抽出して欠損値を削除
        comp_df = df_raw[[label_col] + cols_ctrl + cols_trgt].copy()
        for c in cols_ctrl + cols_trgt:
            comp_df[c] = pd.to_numeric(comp_df[c], errors='coerce')
        
        # 1. 0や4を一旦すべてNaNとして扱う（0を実際の値として計算させないため）
        comp_df[cols_ctrl + cols_trgt] = comp_df[cols_ctrl + cols_trgt].replace({0: np.nan, 4: np.nan})

        # 2. t検定の信頼性を担保するため「どちらかの群で少なくとも2サンプル以上」検出されている行を残す
        mask_valid = (comp_df[cols_ctrl].notna().sum(axis=1) >= 2) | (comp_df[cols_trgt].notna().sum(axis=1) >= 2)
        comp_df = comp_df[mask_valid].copy()

        if len(comp_df) == 0:
            print(f"  No valid data for {target} vs {control}. Skipping.")
            continue

        # 3. 欠損値（検出限界以下）の補完
        # データ全体の最小値を取得し、そこから少し（例: 0.5）引いた値を「ノイズレベルの微小値」として代入する
        min_val = comp_df[cols_ctrl + cols_trgt].min().min()
        impute_val = min_val - 0.5
        comp_df[cols_ctrl + cols_trgt] = comp_df[cols_ctrl + cols_trgt].fillna(impute_val)

        # すでにLog2変換済みのデータを使用するため、再度np.log2()はかけない
        val_ctrl = comp_df[cols_ctrl]
        val_trgt = comp_df[cols_trgt]
        
        # Log2FC = Targetの平均 - Control의 평균 (すでに対数なので引き算でFCになる)
        log2fc = val_trgt.mean(axis=1) - val_ctrl.mean(axis=1)
        with np.errstate(divide='ignore', invalid='ignore'):
            # ウェルチのt検定 (equal_var=False) を使用して、分散の不均一性を考慮
            p_vals = stats.ttest_ind(val_trgt, val_ctrl, axis=1, equal_var=False).pvalue
            neg_log10_p = -np.log10(p_vals)
        
        # Volcanoプロット作成
        v = Volcano(
            protein_id=comp_df[label_col],
            ratio=log2fc,
            pval=neg_log10_p,
            pcutoff=p_cutoff,
            min_log2ratio=min_log2,
            max_log2ratio=max_log2
        )
        
        save_name = f"{target}_vs_{control}_target_is_{target}.png"
        save_path = os.path.join(output_dir, save_name)
        v.get_volcano(target, control, save_path, top_n=10)
        
        # Excel保存 (複数シート)
        p_cutoff_val = -np.log10(p_cutoff)
        fc_col = f'Log2({target}/{control})'
        
        stats_df = comp_df[[label_col]].copy()
        stats_df[fc_col] = log2fc
        stats_df['-log10p'] = neg_log10_p
        
        # 有意なデータの抽出
        df_up = stats_df[(stats_df[fc_col] >= max_log2) & (stats_df['-log10p'] > p_cutoff_val)].sort_values(fc_col, ascending=False)
        df_down = stats_df[(stats_df[fc_col] <= min_log2) & (stats_df['-log10p'] > p_cutoff_val)].sort_values(fc_col, ascending=True)
        
        excel_name = f"stats_{target}_vs_{control}.xlsx"
        excel_path = os.path.join(output_dir, excel_name)
        
        with pd.ExcelWriter(excel_path) as writer:
            stats_df.to_excel(writer, sheet_name='All_Proteins', index=False)
            df_up.to_excel(writer, sheet_name='Significant_Up_Red', index=False)
            df_down.to_excel(writer, sheet_name='Significant_Down_Blue', index=False)
        
        print(f"  Saved plot to {save_name}")
        print(f"  Saved stats to {excel_name} (3 sheets)")

    print(f"\nDone! Results: {output_dir}")
    return output_dir

if __name__ == "__main__":
    FILE_PATH = "raw_data/2026-017N9解析用.xlsx"
    GROUPS = {
        "noCoat": ["1_1", "1_2", "1_3"],
        "PMPC-MNPs-500": ["2_1", "2_2", "2_3"],
        "PMPC-MNPs-100": ["3_1", "3_2", "3_3"]
    }
    COMPARISONS = [
        ("PMPC-MNPs-500", "noCoat"),
        ("PMPC-MNPs-100", "noCoat"),
        ("PMPC-MNPs-100", "PMPC-MNPs-500")
    ]
    run_volcano_analysis(FILE_PATH, GROUPS, COMPARISONS)

