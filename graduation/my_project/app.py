from flask import Flask, render_template, request, redirect, url_for
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import os
import paramiko

app = Flask(__name__, static_folder='/home/c0a20137/graduation/my_project/templates/statics/images') 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_test', methods=['POST'])
def run_test():
    duration_seconds = 20
    # 保存場所を指定してCSVファイルを保存するパス
    csv_file_path = "/home/c0a20137/graduation/test/locust/loadtest_results/result"

    # MasterでのLocust実行とCSVファイルの保存（フォアグラウンド実行）
    command = f"locust -f /home/c0a20137/graduation/my_project/locust/locustfile.py -H http://192.168.100.76:30001 --headless -u 10000 -r 1000 --run-time {duration_seconds}s --csv={csv_file_path}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #監視ソフトウェアを実行
    run_monitor(duration_seconds)
    
    create_graph()
    
    return redirect(url_for('show_graph'))

# 画像ファイルが保存されているディレクトリのパス
image_dir = '/home/c0a20137/graduation/test/monitor_data/images'

@app.route('/show_graph')
def show_graph():
    # 指定ディレクトリ内の画像ファイルを取得
    image_files = get_image_files(image_dir)

    # テンプレートに画像ファイルのリストを渡す
    return render_template('index.html', image_files=image_files)

def get_image_files(directory):
    image_files = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append(filename)
    return image_files

def create_graph():
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
        plt.plot(pod_data['timestamp'], pod_data['cpu_usage(m)'], label=pod_name)

    plt.xlabel('Timestamp')
    plt.ylabel('CPU Usage (m)')
    plt.title('CPU Usage Over Time')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 横軸を10分割して表示
    x_ticks = plt.gca().get_xticks()
    x_ticks = x_ticks[::len(x_ticks) // 10]
    plt.gca().set_xticks(x_ticks)

    # グラフをPNGファイルとして保存
    output_file = f'{output_path}cpu_usage_graph.png'
    plt.savefig(output_file, dpi=300)  # 保存ファイル名とDPIを指定

    # 各Podごとに個別のグラフを生成して保存
    for pod_name in pod_names:
        pod_data = df[df['pod'] == pod_name]

        # グラフを描画
        plt.figure(figsize=(12, 6))
        plt.plot(pod_data['timestamp'], pod_data['cpu_usage(m)'])
        plt.xlabel('Timestamp')
        plt.ylabel('CPU Usage (m)')
        plt.title(f'CPU Usage Over Time - {pod_name}')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 横軸を10分割して表示
        x_ticks = plt.gca().get_xticks()
        x_ticks = x_ticks[::len(x_ticks) // 10]
        plt.gca().set_xticks(x_ticks)

        # グラフをPNGファイルとして保存
        output_file = f'{output_path}{pod_name}_cpu_usage_graph.png'
        plt.savefig(output_file, dpi=300)  # 保存ファイル名とDPIを指定
        plt.close()  # メモリリークを防ぐためにグラフを閉じる
        
        
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


if __name__ == '__main__':
    app.run(debug=True)
