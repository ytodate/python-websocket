# coding: utf-8
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__) # Flask動かす時のおまじない
app.config['SECRET_KEY'] = 'hogehugahage' # セキュリティのおまじない
socketio = SocketIO(app, async_mode=None) # async_mode

class SiteInfo:
    title = 'ページタイトル'

# render index.html & get form data
@app.route("/", methods=['GET','POST'])
def get_form():
    try:
        value_single = request.form['single']
    except:
        value_single = None
    try:
        value_list = request.form.getlist('list')
    except:
        value_list = []
    return render_template('index.html',
                           title = SiteInfo.title,
                           value_list = value_list,
                           value_single = value_single,
                           )

# websocket sample
# バックグラウンドでサーバー側から常に情報を与える
def background(comment):
    num = 0
    while True:
        socketio.sleep(1)
        num += 1
        content = "<span>%d%s</span>" % (num,comment)
        '''my_countに送信。後述の@socketio.on()で指定していないときは、socketio.emitとし、namespaceを指定する必要あり。
        namespaceとmy_countについてはsocket.html内のjQueryで受け取るためのラベル
        contentが送信するデータ'''
        socketio.emit('my_count', {'data': content}, namespace='/demo')

# フォームからの入力もリアルタイムに受け取る
@app.route('/websocket',methods=['GET','POST'])
def websocket():
    '''background(comment)を実行
    ページに「○秒が経過」と毎秒表示'''
    socketio.start_background_task(target=background, comment='秒が経過')
    return render_template('socket.html',
                           async_mode = socketio.async_mode,
                           title = SiteInfo.title,
                           )

# socketioの設定
@socketio.on('receive_content', namespace='/demo') # socket.html側の/demoからreceive_contentに対して送られてきた場合
def send_content(sent_data): # sent_data:受け取ったデータの名前を好きに設定できます。
    content = '<li>%s</li>' % sent_data['data'] # socket.html側で{data:content}としているのでこうなる。
    '''データをsocket.htmlのmy_contentに送信。
    broadcast=Trueは同じnamespaceにアクセスしている人全員の画面に反映
    '''
    emit('my_content', {'data': content}, broadcast=False)

if __name__ == "__main__":
    print("saver start...")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
