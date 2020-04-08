# atsumori_kabu_bot

## ブランチの説明
- master ボット本体に反映されるブランチ
- test テスト用ブランチ。基本は各自ブランチを分けて作業し、testにマージしテスト用Botで試運転した後masterに反映させる。

## gitの設定について
gitの設定がファイル名の大文字小文字を無視する設定になっているとうまく動かないことがある。可能であればコマンドラインで
```$ git config -l --local | grep core.ignorecase```
を試し、結果が
```core.ignorecase=true```
であれば、
```$ git config core.ignorecase false```
を実行し、大文字小文字の区別を無視する設定を無効にする。
