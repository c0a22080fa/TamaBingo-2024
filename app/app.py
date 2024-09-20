from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import qrcode
import io
from .database import connect_db, check_db,add_user,del_user


# ビンゴシートの状態を保持するためのリスト
bingo_sheet =[[False,False,False],
              [False,False,False],
              [False,False,False]] # 3x3 ビンゴシート


app = Flask(__name__, static_folder='./static')
app.secret_key = 'your_secret_key'
# font = cv2.FONT_HERSHEY_SIMPLEX
FILE_PNG_AB = 'qrcode_AB.png'

def bingo_check(bingo_list):
    '''
    引数：なし
    出力：ビンゴの数
    '''
    ans=0
    for i in range(3):
        if all(bingo_list[i]):
            ans+=1
            print(1)
        if all(row[i] for row in bingo_list):
            ans+=1
            print(2)
    if bingo_list[0][0] and bingo_list[1][1] and bingo_list[2][2]:
        ans+=1
        # print(3)
    if bingo_list[2][0] and bingo_list[1][1] and bingo_list[0][2]:
        ans+=1
        # print(3)
    return ans

# QRコード生成用関数
def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    return img

@app.route('/top')
def login_after():#ログイン済み確認
    if 'username' in session:
        return render_template('top.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/bingo')
def bingo():
    return render_template('bingo.html')

@app.route('/generate_qr/<int:cell_id>')
def generate_qr_code(cell_id):
    # QRコードに埋め込むURLを設定
    url = str(cell_id)  # QRコードにはセルIDだけを埋め込む
    img = generate_qr(url)

    # QRコード画像をバイト形式で返す
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/stamp/<int:cell_id>')
def stamp(cell_id):
    # call_idをindexに変換
    index1 = int((cell_id - 1) / 3)
    index2 = int((cell_id - 1) % 3)
    if cell_id <= 9:
        bingo_sheet[index1][index2] = True
        return jsonify(success=True, cell_id=cell_id)

    # セルIDの範囲チェック
    if 1 <= cell_id <= 9:
        bingo_sheet[cell_id - 1] = True
        return jsonify(success=True, cell_id=cell_id)
    else:
        return jsonify(success=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = connect_db(username, password)
        if(result):
            session['username'] = username
            return render_template('top.html')
    return render_template('login.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        if(password == password2):
            add_user(username, password)
            return redirect(url_for('login'))
        
    return render_template('add.html')

@app.route('/deleate', methods=['GET', 'POST'])
def deleate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = connect_db(username, password)
        if(result):
            del_user(username,password)
            return redirect(url_for('logout'))
    return render_template('deleate.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/bingo_spot', methods=['GET','post'])
def index_3(num):
    global bingo_sheet
    num=int(num)
    bingo_sheet[int(num/3)][num%3]=True
    return render_template('bingo_spot.html')


@app.route('/<sample_name>', methods=['GET', 'POST'])
def allpass(sample_name):
    global bingo_sheet 
    bingo_num=bingo_check(bingo_sheet)
    return render_template(f'{sample_name}.html',bingo_sheet=bingo_sheet,bingo_num=bingo_num)

if __name__ == '__main__':
    app.run( debug=True)


