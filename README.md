# lolog
ロードス島戦記オンライン http://lodoss.pmang.jp をキャプチャーした動画から与ダメージを検出し、csv形式で書き出すコマンドラインツールです。まだまだ認識精度と動作速度に問題があるため、検出された数字は参考程度にしてください。

## 動作環境
Python3 + OpenCV3が必要です。Mac OS Xがメインですが、一応Windows10でも動作を確認しました。また使用者に若干のコマンドライン知識が求められます。

## 環境構築

### Windows

https://www.continuum.io/downloads のAnaconda for WindowsからPYTHON 3.5の64bit版をインストールする（入れた後、再起動が必要かも？）

http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
から
opencv_python-3.1.0+contrib-cp35-cp35m-win_amd64.whl
をダウンロードする。

コマンドプロンプトから
```
cd （保存した場所）
pip install opencv_python-3.1.0+contrib-cp35-cp35m-win_amd64.whl
```
を実行。

### Mac OS X

```
brew tap homebrew/science
brew install python3
brew install numpy --with-python3
brew link numpy
brew install opencv3 --with-python3 --with-ffmpeg —without-python
brew link opencv3 --force
```

### lologのインストール
今見てるこのページ https://github.com/ymmtmdk/lolog の一番右上から少し下にあるDownload ZIPをクリックして好きな場所で解凍してください。

## 動作確認
```
cd (先ほど解凍したディレクトリ)
python lolog.py video/sample.mkv
```

を実行。

```
frame: 0 95
frame: 16 147
frame: 18 147
frame: 5 71
frame: 6 71
frame: 7 71
frame,0,damage,95,critical,False,miss,False
frame,6,damage,71,critical,False,miss,False
frame,16,damage,147,critical,True,miss,False
```

といった出力とlogディレクトリに日付のついたcsvがあれば成功です。

## 対象となる動画
ffmpegでキャプチャーしたロスレス（無劣化）の動画のみで動作を確認してます。圧縮された動画でも動かないわけではないですが、圧縮具合によって検出精度が変わるので注意してください。

### ffmpegでのキャプチャー例

https://ffmpeg.zeranoe.com/builds/ から64-bit Downloadsの一番上のDownload FFmpeg git-*64-bit Staticをダウンロードして解凍。

ロードス島戦記オンラインのクライアントを起動。

```
cd (先ほど解凍したディレクトリ)
cd bin
ffmpeg -f gdigrab -show_region 1 -framerate 30 -video_size 300x300 -offset_x 500 -offset_y 400 -i desktop -c:v libx264 -qp 0 -preset ultrafast capture.mkv
```

ffmpegがキャプチャー範囲を表す枠を出してくれてるのでその中にダメージ表示が収まるようにキャラクターを操作してください。

コマンドプロンプトでqを入力するとキャプチャーを停止します。

```
python lolog.py （どっか）/capture.mkv
```

で動画を解析します。

## 高速な解析

ゲーム画面をフルサイズで解析対象にするとものすごく時間がかかります。
キャプチャー段階、もしくは解析段階でサイズを制限することが高速化のコツです。解析段階でのサイズの制限については下のコマンドラインオプションを参照してください。

## コマンドラインオプション

```
Usage: lolog.py [options] [video file]

Options:
  -s START, --start=START
　　対象の動画の解析開始時点をフレーム数で指定します
  -l LENGTH, --length=LENGTH
　　対象の動画の解析開始時点から解析するフレーム数を指定します
  -X OFFSET_X, --offset_x=OFFSET_X
　　対象の動画の解析対象とするx座標を指定します
  -Y OFFSET_Y, --offset_y=OFFSET_Y
　　対象の動画の解析対象とするy座標を指定します
  --crop_size=CROP_SIZE
　　対象の動画の解析対象とする範囲を指定します
```

### 実行例
```
python lolog.py capture.mkv
```
```
python lolog.py -s 10 -l 1000 -X 100 -Y 100 --crop_size=200x200 capture.mkv
```
