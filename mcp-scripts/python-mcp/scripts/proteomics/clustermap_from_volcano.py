import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime
import numpy as np

# --- 設定 ---
input_file = 'raw_data/2026-017N9解析用.xlsx'
stats_file = 'output_plot/20260420_213409/stats_free_500_vs_noCoat.xlsx'
protein_name_column = 'Protein.Names' 

output_base_dir = 'output_plot'

# ユーザー指定のマッピング (プロテイン名は一切変更していません)
FUNCTION_MAPPING = {
    'Opsonization (Complement)': [
        "C1QB_MOUSE","CO3_MOUSE","C1QA_MOUSE","C1QC_MOUSE","CFAH_MOUSE","CFAB_MOUSE","CO8B_MOUSE","CO5_MOUSE","CFAI_MOUSE","CR1L_MOUSE","CO4B_MOUSE","C1RA_MOUSE","CO8G_MOUSE","CFAD_MOUSE","C4BPA_MOUSE","CO8A_MOUSE","CS1A_MOUSE","CO9_MOUSE","DAF1_MOUSE","CO2_MOUSE","C1QBP_MOUSE","CS1B_MOUSE",
    ],
    'Opsonization (Ig;Immunoglobulin/FcR)': [
            "IGHM_MOUSE","KV1A1_MOUSE","HVM18_MOUSE;HVM19_MOUSE;HVM21_MOUSE;HVM22_MOUSE;HVM25_MOUSE","KV5A6_MOUSE","KV2A7_MOUSE","IGHG3_MOUSE","IGJ_MOUSE","KV5AB_MOUSE;KV5AC_MOUSE","HVM27_MOUSE;HVM28_MOUSE;HVM30_MOUSE;HVM32_MOUSE","IGH1M_MOUSE;IGHG1_MOUSE","IGKC_MOUSE","HVM53_MOUSE","KV3A8_MOUSE","HVM57_MOUSE","LAC2_MOUSE","HVM17_MOUSE","LAC1_MOUSE","KV5A3_MOUSE","IGG2B_MOUSE","KV5A9_MOUSE","KV6A6_MOUSE;KV6A7_MOUSE;KV6A9_MOUSE;KV6AA_MOUSE","HVM36_MOUSE;HVM37_MOUSE;HVM38_MOUSE;HVM39_MOUSE;HVM42_MOUSE","KV5A7_MOUSE","GCAA_MOUSE;GCAM_MOUSE","KV5A1_MOUSE","IGHA_MOUSE","KV2A6_MOUSE","HVM35_MOUSE","KV5AA_MOUSE","KV4A1_MOUSE","KV5A4_MOUSE","KV3AM_MOUSE","LAC3_MOUSE","HVM15_MOUSE","KV2A5_MOUSE","PIGR_MOUSE","HVM51_MOUSE","HVM14_MOUSE","HVM56_MOUSE","IGBP1_MOUSE","FCGRN_MOUSE","HVM12_MOUSE;HVM13_MOUSE","LV2A_MOUSE;LV2B_MOUSE","HVM60_MOUSE","KV6AB_MOUSE","KV3A1_MOUSE;KV3A3_MOUSE","KV6A1_MOUSE;KV6A2_MOUSE;KV6A3_MOUSE;KV6A4_MOUSE;KV6A5_MOUSE","KV3AJ_MOUSE","HVM10_MOUSE;HVM49_MOUSE","VSIG8_MOUSE","KV3AC_MOUSE;KV3AD_MOUSE;KV3AE_MOUSE;KV3AG_MOUSE","KV2A2_MOUSE","HVM43_MOUSE;HVM44_MOUSE","LV1A_MOUSE;LV1B_MOUSE;LV1D_MOUSE;LV1E_MOUSE"
    ],
    'Lipoprotein Uptake (Apo)': [
    "APOA1_MOUSE","APOC1_MOUSE","APOE_MOUSE","APOA4_MOUSE","APOC3_MOUSE","APOC4_MOUSE","APOB_MOUSE","APOC2_MOUSE","APOD_MOUSE","APOA2_MOUSE","APOM_MOUSE","APOA5_MOUSE","APOF_MOUSE"
    ],
    'Coagulation/Inflam': [
        "FA5_MOUSE","FA12_MOUSE","F13A_MOUSE","FA10_MOUSE","FA11_MOUSE","FA7_MOUSE","FA9_MOUSE","FA8_MOUSE",
    ],
    
    'adhesive protein': [
        "FINC_MOUSE","VTNC_MOUSE","TSP1_MOUSE","TSP4_MOUSE","OSTP_MOUSE","TENA_MOUSE",
    ],

    'relative C-reactive protein': [
        "CRP_MOUSE","C1QB_MOUSE","C1QA_MOUSE","C1QC_MOUSE","C1QBP_MOUSE","CFAH_MOUSE","C1RA_MOUSE","CS1A_MOUSE","CO4B_MOUSE","CO2_MOUSE","CO3_MOUSE"
    ]
}

# 順序を保持
category_order = list(FUNCTION_MAPPING.keys())
protein_to_category = {}
for cat in category_order:
    for p_entry in FUNCTION_MAPPING[cat]:
        for p in p_entry.split(';'):
            protein_to_category[p.strip().upper()] = cat

def run_clustermap_analysis(input_file, stats_file, protein_name_column='Protein.Names', output_base_dir=None, function_mapping=None, groups=None, group_order=None):
    """
    有意なタンパク質のヒートマップ（Clustermap）を作成します。
    
    Args:
        input_file: 元データのExcelファイルの絶対パス。
        stats_file: 統計結果Excelファイルの絶対パス。
        protein_name_column: タンパク質名カラム名。
        output_base_dir: 結果の保存先ベースディレクトリ（絶対パス推奨）。
        function_mapping: カテゴリマッピング（Noneの場合はデフォルトを使用）。
        groups: 群定義（Noneの場合はデフォルトを使用）。
        group_order: 表示する群の順序（Noneの場合はデフォルトを使用）。
    """
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return None
    if not os.path.exists(stats_file):
        print(f"Error: {stats_file} not found.")
        return None

    # 出力先ディレクトリの決定
    if output_base_dir is None:
        output_base_dir = os.path.join(os.getcwd(), "output_plot")
    else:
        output_base_dir = os.path.abspath(output_base_dir)

    if function_mapping is None:
        function_mapping = FUNCTION_MAPPING
    
    category_order = list(function_mapping.keys())
    protein_to_category = {}
    for cat in category_order:
        for p_entry in function_mapping[cat]:
            for p in p_entry.split(';'):
                protein_to_category[p.strip().upper()] = cat

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base_dir, f"{timestamp}_heatmap_sig_function")
    os.makedirs(output_dir, exist_ok=True)

    # 有意なタンパク質リストの読み込み
    print(f"Loading significant proteins from {stats_file}...")
    df_up = pd.read_excel(stats_file, sheet_name='Significant_Up_Red')
    df_down = pd.read_excel(stats_file, sheet_name='Significant_Down_Blue')
    sig_proteins = set(df_up[protein_name_column].astype(str).unique()) | \
                   set(df_down[protein_name_column].astype(str).unique())

    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)

    # --- 1. カラム定義とドロップアウト ---
    if group_order is None:
        group_order = ['noCoat', 'PMPC-MNPs-100', 'PMPC-MNPs-500']
    if groups is None:
        groups = {
            'noCoat': ['1_1', '1_2', '1_3'],
            'PMPC-MNPs-100': ['3_1', '3_2', '3_3'],
            'PMPC-MNPs-500': ['2_1', '2_2', '2_3']
        }
    
    all_data_cols = [c for group in groups.values() for c in group if c in df.columns]
    for col in all_data_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 「4」が含まれる行を除外
    df = df[~(df[all_data_cols] == 4).any(axis=1)].copy()

    # --- 2. カテゴリ紐付けと平均計算 ---
    def get_category(name):
        if not isinstance(name, str): return None
        parts = [p.strip().upper() for p in name.split(';')]
        for p in parts:
            if p in protein_to_category:
                return protein_to_category[p]
        return None

    df['Category'] = df[protein_name_column].apply(get_category)
    
    # カテゴリに該当し、かつ有意差リストに含まれるもののみ抽出
    df_filtered = df[
        (df['Category'].notnull()) & 
        (df[protein_name_column].astype(str).isin(sig_proteins))
    ].copy()
    
    df_filtered['Category'] = pd.Categorical(df_filtered['Category'], categories=category_order, ordered=True)
    
    for group_name, cols in groups.items():
        df_filtered[group_name] = df_filtered[cols].mean(axis=1)

    if df_filtered.empty:
        print("No proteins matched both function mapping and significance criteria.")
        return output_dir

    # 重複排除とソート
    heatmap_data = df_filtered.groupby([protein_name_column, 'Category'], observed=True)[group_order].mean().reset_index()
    heatmap_data = heatmap_data.sort_values(['Category', protein_name_column])
    heatmap_data = heatmap_data.set_index(protein_name_column)
    plot_data = heatmap_data[group_order]

    # --- 3. ヒートマップの作成 (Clustermap, クラスタリングなし) ---
    calc_height = max(12, 2 + len(plot_data) * 0.25)
    sns.set(font_scale=0.8)
    
    g = sns.clustermap(
        plot_data,
        cmap='RdYlBu_r',
        z_score=0,          # 行方向の標準化
        row_cluster=False,  # 行の順番を固定
        col_cluster=False,  # 列の順番も固定
        figsize=(12, calc_height),
        annot=False,
        cbar_kws={'label': 'Z-score (Intensity)'},
        cbar_pos=(0.02, 0.8, 0.02, 0.15), # 凡例の幅を 0.02 にして細く設定
        yticklabels=True
    )

    # --- 4. ブラケット（括りラベル）の描画 ---
    ax = g.ax_heatmap
    n_cols = len(group_order)
    current_y = 0
    
    for cat in category_order:
        count = len(heatmap_data[heatmap_data['Category'] == cat])
        if count == 0: continue
        
        # y座標
        start_y = current_y
        end_y = current_y + count
        mid_y = current_y + count / 2
        
        # ブラケット位置
        x_pos = n_cols + 0.1
        bracket_width = 0.5
        
        # clip_on=False でヒートマップの枠外に描画
        ax.plot([x_pos, x_pos + bracket_width], [start_y, start_y], color='black', lw=1.5, clip_on=False)
        ax.plot([x_pos, x_pos + bracket_width], [end_y, end_y], color='black', lw=1.5, clip_on=False)
        ax.plot([x_pos + bracket_width, x_pos + bracket_width], [start_y, end_y], color='black', lw=1.5, clip_on=False)
        
        # カテゴリラベル
        ax.text(x_pos + bracket_width + 0.2, mid_y, cat, 
                va='center', ha='left', fontsize=12, fontweight='bold', color='black', clip_on=False)
        
        current_y += count

    # レイアウト調整
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=0) 
    plt.subplots_adjust(right=0.65) # 右側にラベルを表示するスペースを確保
    
    output_path = os.path.join(output_dir, 'heatmap_function_accurate.png')
    g.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Heatmap saved to: {output_path}")

    # ソースデータも保存
    heatmap_data.to_excel(os.path.join(output_dir, 'heatmap_source_data_accurate.xlsx'))
    return output_dir

if __name__ == "__main__":
    input_file = 'raw_data/2026-017N9解析用.xlsx'
    stats_file = 'output_plot/20260420_213409/stats_free_500_vs_noCoat.xlsx'
    run_clustermap_analysis(input_file, stats_file)

