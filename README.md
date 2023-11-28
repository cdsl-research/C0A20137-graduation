# PSSP
## 用途
負荷試験からグラフ作成までを自動化するWEBアプリケーション．
Locustを用いて「Sock Shop」に負荷試験を行い，同時にPodのCPU使用量とサービス内のPod数を監視しCSVファイル形式で時系列に保存
負荷試験終了後，取得したデータをもとにサービスごとに時系列グラフを作成．
リクエスト数の増加に敏感に反応するサービスとエラーが発生したリクエストに関係するサービスのCPU使用量のグラフを表示する

## 使用方法
以下のコマンドでPSSPを起動し，WEBページを表示．

```
python3 app.py
```

![use-case](https://github.com/cdsl-research/C0A20137-graduation/assets/68420314/7966e02e-18ec-472b-89c0-3e577565bfb6)
