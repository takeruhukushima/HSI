import urllib.request
import json
import time
import torch
import esm
import numpy as np
import pandas as pd
import umap
import hdbscan
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
import os
from datetime import datetime

def get_uniprot_sequence(protein_id):
    """UniProt IDからアミノ酸配列を取得する"""
    # 複数のIDが分かれている場合（例: ID1;ID2）は最初のものを使用
    main_id = protein_id.split(';')[0].split('_')[0]
    url = f"https://rest.uniprot.org/uniprotkb/search?query=gene:{main_id}+AND+organism_id:10090&format=json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data['results']:
                return data['results'][0]['sequence']['value']
    except Exception as e:
        print(f"Error fetching sequence for {protein_id}: {e}")
    return None

def run_po_analysis(stats_file, anchors=["CLUS_MOUSE"], output_base_dir=None):
    """
    ESM-2埋め込みとUMAP/HDBSCANを用いて、特定のアンカータンパク質に対する吸着予測（PO解析）を行います。
    
    Args:
        stats_file: 解析対象のExcelファイルの絶対パス。
        anchors: 基準となるアンカータンパク質のリスト。
        output_base_dir: 結果の保存先ベースディレクトリ（絶対パス推奨）。
    """
    if not os.path.exists(stats_file):
        print(f"Error: {stats_file} not found.")
        return None

    # 出力先ディレクトリの決定
    if output_base_dir is None:
        output_base_dir = os.path.join(os.getcwd(), "output_plot")
    else:
        output_base_dir = os.path.abspath(output_base_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base_dir, f"{timestamp}_po_analysis")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading stats from {stats_file}...")
    df = pd.read_excel(stats_file)
    # Protein.Names または ID カラムを探す
    protein_col = 'Protein.Names' if 'Protein.Names' in df.columns else (df.columns[0] if 'Protein' not in df.columns else 'Protein')
    if protein_col != 'Protein':
        df['Protein'] = df[protein_col]

    # Regulation (Up/Down) の判定
    if 'Log2' in df.columns: # 仮の判定
        df['Regulation'] = np.where(df.iloc[:, 1] > 0, 'Up', 'Down')
    else:
        df['Regulation'] = 'Unknown'

    print("Fetching protein sequences and generating embeddings (ESM-2)...")
    # ESM-2 モデルのロード (最も小さい 35M パラメータモデルを使用)
    model, alphabet = esm.pretrained.esm2_t6_8M_UR50D()
    batch_converter = alphabet.get_batch_converter()
    model.eval()

    sequences = []
    valid_proteins = []
    for p in df['Protein'].head(100): # 重いので上位100個に限定
        seq = get_uniprot_sequence(p)
        if seq:
            sequences.append((p, seq))
            valid_proteins.append(p)
        time.sleep(0.1) # Rate limit 対策

    if not sequences:
        print("No sequences found.")
        return None

    # バッチ処理で埋め込みを作成
    batch_labels, batch_strs, batch_tokens = batch_converter(sequences)
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[6], return_contacts=False)
    token_representations = results["representations"][6]

    # 配列全体の表現（平均プーリング）
    X = []
    for i, (_, seq) in enumerate(sequences):
        X.append(token_representations[i, 1 : len(seq) + 1].mean(0).numpy())
    X = np.array(X)

    # 有効なタンパク質のみに絞り込む
    df = df[df['Protein'].isin(valid_proteins)].reset_index(drop=True)
    
    # UMAP & HDBSCAN
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(X)
    df['UMAP1'] = embedding[:, 0]
    df['UMAP2'] = embedding[:, 1]

    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
    df['Cluster'] = clusterer.fit_predict(X)

    # アンカー処理
    valid_anchors = [a for a in anchors if a in df['Protein'].values]

    if valid_anchors:
        sim_scores_list = []
        anchor_clusters = []

        for anchor in valid_anchors:
            anchor_idx = df[df['Protein'] == anchor].index[0]
            anchor_vector = X[anchor_idx].reshape(1, -1)
            anchor_clusters.append(df.loc[anchor_idx, 'Cluster'])

            similarities = cosine_similarity(X, anchor_vector).flatten()
            sim_scores_list.append(np.clip(similarities, 0, 1) * 80)

        max_sim_scores = np.max(sim_scores_list, axis=0)
        valid_anchor_clusters = [c for c in set(anchor_clusters) if c != -1]
        cluster_bonus = np.where(df['Cluster'].isin(valid_anchor_clusters) & (df['Cluster'] != -1), 20, 0)
        df['PO_Score'] = np.round(max_sim_scores + cluster_bonus, 2)
    else:
        print(f"⚠️ 指定されたアンカータンパク質 {anchors} がデータ内に一つも見つかりません。")
        df['PO_Score'] = 0

    df = df.sort_values(by='PO_Score', ascending=False).reset_index(drop=True)
    output_filename = os.path.join(output_dir, "PO_Analysis_Results.csv")
    df.to_csv(output_filename, index=False)
    
    # 可視化
    df['Cluster'] = df['Cluster'].astype(str)
    fig = px.scatter(
        df, x='UMAP1', y='UMAP2',
        color='Cluster', symbol='Regulation',
        hover_name='Protein',
        hover_data={'UMAP1': False, 'UMAP2': False, 'Cluster': True, 'Regulation': True, 'PO_Score': True},
        title=f'PO Analysis: Multi-Anchor Adsorption Prediction',
        width=1000, height=800
    )

    anchor_data = df[df['Protein'].isin(valid_anchors)]
    if not anchor_data.empty:
        fig.add_scatter(
            x=anchor_data['UMAP1'], y=anchor_data['UMAP2'],
            mode='markers+text',
            marker=dict(size=20, symbol='star', color='gold', line=dict(width=2, color='black')),
            text=["ANCHOR" for _ in range(len(anchor_data))], textposition="top center",
            name="Anchors"
        )

    fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(template='plotly_white')
    
    html_path = os.path.join(output_dir, 'po_analysis_plot.html')
    fig.write_html(html_path)
    
    print(f"\n=== ✨ PO解析システム 処理完了 ✨ ===")
    return output_dir

if __name__ == "__main__":
    stats_file = 'output_plot/20260420_213409/stats_PMPC-MNPs-500_vs_noCoat.xlsx'
    run_po_analysis(stats_file)
