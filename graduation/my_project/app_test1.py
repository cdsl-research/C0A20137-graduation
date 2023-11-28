from flask import Flask, render_template, request, redirect, url_for
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import threading
import numpy as np

app = Flask(__name__, static_folder='/home/c0a20137/graduation/my_project/templates/statics/images') 

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/run_test', methods=['POST'])
def run_test():
    duration_seconds = 100
    et = int(time.time()) + duration_seconds
    csv_file_path = "/home/c0a20137/graduation/test/locust/loadtest_results/result"

    # 別々のスレッドで実行する関数を定義
    def run_locust():
        command1 = f"locust -f /home/c0a20137/graduation/test/locust/locustfile.py -H http://192.168.100.76:30001 --headless -u 10000 -r 110 --run-time {duration_seconds}s --csv={csv_file_path}"
        os.system(command1)

    def run_and_monitor():
        run_monitor(duration_seconds)

    # 各関数を実行するスレッドを作成
    thread_1 = threading.Thread(target=run_locust)
    thread_2 = threading.Thread(target=run_and_monitor)

    # 両方のスレッドを開始
    thread_1.start()
    thread_2.start()

    # 両方のスレッドが終了するのを待つ
    thread_1.join()
    thread_2.join()
    create_graph()

    return redirect(url_for('show_graph'))

def run_monitor(duration_seconds):
    # 出力ファイルパス
    output_file = "/home/c0a20137/graduation/test/monitor_data/data.csv"

    # シェルスクリプトを実行するコマンド
    command = f'''
        #!/bin/bash
        # CSVファイルのヘッダを作成
        echo "timestamp,pod,cpu_usage(m),memory_usage(Mi)" > {output_file}

        # 開始時刻
        start_time=$(date +%s)

        while :
        do
            current_time=$(date +%s)
            elapsed_time=$((current_time - start_time))

            # 指定した時間を超えたら終了
            if [ "$elapsed_time" -ge "{duration_seconds}" ]; then
                break
            fi

            timestamp=$(date '+%Y-%m-%d %H:%M:%S')

            # すべてのPodのリソース使用量を取得し、単位を取り除く
            kubectl top pod -n sock-shop --no-headers 2>/dev/null | while read -r pod cpu_usage memory_usage; do
                cpu_usage=$(echo "$cpu_usage" | tr -d 'm')
                memory_usage=$(echo "$memory_usage" | tr -d 'Mi')
                echo "$timestamp,$pod,$cpu_usage,$memory_usage" >> {output_file}
            done &  # バックグラウンドで実行

            sleep 1
        done
    '''

    # スクリプトを一時ファイルに書き込む
    script_file = "temp_script.sh"
    with open(script_file, "w") as f:
        f.write(command)

    # シェルスクリプトを実行
    subprocess.run(f"bash {script_file}", shell=True)

    # 一時ファイルを削除
    os.remove(script_file)


# 画像ファイルが保存されているディレクトリのパス
image_dir = '/home/c0a20137/graduation/my_project/templates/statics/images/'

@app.route('/show_graph')
def show_graph():
    # 相関係数に基づいてソートした辞書を取得
    image_order = correlation()
    print(image_order)
    return render_template('index.html', image_files=image_order)


def get_image_files(directory):
    image_files = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append(filename)
    return image_files



def create_graph():
    # グラフ全体の文字サイズを設定
    plt.rc('font', size=18)  # フォントサイズを設定
    plt.rc('axes', labelsize=18)  # x軸とy軸のラベルのフォントサイズを設定
    plt.rc('xtick', labelsize=16)  # x軸の目盛りのフォントサイズを設定
    plt.rc('ytick', labelsize=16)  # y軸の目盛りのフォントサイズを設定

    # CSVファイルのパス（適切なパスに変更してください）
    csv_file = "/home/c0a20137/graduation/test/monitor_data/data.csv"

    output_path = "/home/c0a20137/graduation/my_project/templates/statics/images/"

    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)

    # グラフに表示するデータを選択（podごとにデータを分割）
    pod_names = df['pod'].unique()

    # グラフを描画
    plt.figure(figsize=(12, 6))

    for pod_name in pod_names:
        pod_data = df[df['pod'] == pod_name]
        
        # Convert the timestamp to elapsed time in seconds
        elapsed_time = (pd.to_datetime(pod_data['timestamp']) - pd.to_datetime(pod_data['timestamp'].iloc[0])).dt.total_seconds()
        
        plt.plot(elapsed_time, pod_data['cpu_usage(m)'], label=pod_name)

    plt.xlabel('Elapsed Time (seconds)')
    plt.ylabel('CPU Usage (m)')
    plt.title('Sock Shop all Pods')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    # グラフをPNGファイルとして保存
    output_file = f'{output_path}sock shop.png'
    plt.savefig(output_file, dpi=300)  # 保存ファイル名とDPIを指定

    # 各Podごとに個別のグラフを生成して保存
    for pod_name in pod_names:
        pod_data = df[df['pod'] == pod_name]
        
        # Convert the timestamp to elapsed time for individual graphs
        elapsed_time = (pd.to_datetime(pod_data['timestamp']) - pd.to_datetime(pod_data['timestamp'].iloc[0])).dt.total_seconds()

        # グラフを描画
        plt.figure(figsize=(12, 6))
        plt.plot(elapsed_time, pod_data['cpu_usage(m)'])
        plt.xlabel('Elapsed Time (seconds)')
        plt.ylabel('CPU Usage (m)')
        plt.title(f'{pod_name}')
        plt.tight_layout()

        # グラフをPNGファイルとして保存
        output_file = f'{output_path}{pod_name}.png'
        plt.savefig(output_file, dpi=300)  # 保存ファイル名とDPIを指定
        plt.close()  # メモリリークを防ぐためにグラフを閉じる


def correlation():
    # data1: podごとのCPU使用量のCSVファイルを読み込みます
    data1 = pd.read_csv("/home/c0a20137/graduation/test/monitor_data/data.csv")
    # data2: Locustによる負荷試験の結果のCSVファイルを読み込みます
    data2 = pd.read_csv("/home/c0a20137/graduation/test/locust/loadtest_results/result_stats_history.csv")

    # 時刻のフォーマットを調整します
    data1['timestamp'] = pd.to_datetime(data1['timestamp'])
    data2['Timestamp'] = pd.to_datetime(data2['Timestamp'], unit='s')  # Unixタイムスタンプからの変換

    # data1からすべての異なるPod名を取得
    unique_pod_names = data1['pod'].unique()

    # 辞書型を初期化
    correlation_dict = {}

    # 各Podごとにデータの統合と相関係数の計算を行う
    for pod_name in unique_pod_names:
        data1_pod = data1[data1['pod'] == pod_name]
        data2_pod = data2  # data2はすべてのPodに関するデータを持っているため変更不要
        
        # data1とdata2を時刻に基づいて統合
        merged_data = pd.merge(data1_pod, data2_pod, how='inner', left_on='timestamp', right_on='Timestamp')

        # Requests/s と CPU使用量(m) の列を取得します
        requests_per_s = merged_data["Requests/s"]
        cpu_usage = merged_data["cpu_usage(m)"]

        # 相関係数を計算します
        correlation = np.corrcoef(requests_per_s, cpu_usage)[0, 1]
        
        # NaNの場合は0に置き換え
        if np.isnan(correlation):
            correlation = 0
        
        # 辞書型にPod名と相関係数を追加
        correlation_dict[pod_name] = correlation

    # 相関係数で降順にソート
    sorted_correlation = dict(sorted(correlation_dict.items(), key=lambda item: item[1], reverse=True))
    sorted_keys = list(sorted_correlation.keys())
    sorted_tuple = tuple(sorted_keys)
    sorted_images = []
    for i in range(len(sorted_tuple)):
        
        sorted_images.append(f"{sorted_tuple[i]}.png")
    sorted_images.insert(0,"sock shop.png")
    return sorted_images

if __name__ == '__main__':
    app.run(debug=True, port=5001)
