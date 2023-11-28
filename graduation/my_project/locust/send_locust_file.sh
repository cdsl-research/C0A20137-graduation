#!/bin/bash

# 送信元のディレクトリパス
dir="/home/c0a20137/locust"

# 送信先のIPアドレスリスト
ip_addresses=("192.168.100.145" "192.168.100.164")

# ファイル送信の関数
send_files() {
  local source=$1
  local destination=$2
  scp "$source" "$destination"
}

# 送信先のIPアドレスリストに対してファイルを送信
for ip_address in "${ip_addresses[@]}"
do
  for file in "$dir"/*
  do
    if [ -f "$file" ]; then
      filename=$(basename "$file")
      destination="$ip_address:$dir/$filename"
      send_files "$file" "$destination"
    fi
  done
done
