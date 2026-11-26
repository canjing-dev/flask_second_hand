from sqlalchemy.orm import sessionmaker
from flask import Flask, request, redirect, render_template, session,current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

#Flask框架应用
app = Flask(__name__)
#用于session签名防止篡改
app.secret_key = 'suibianyigeanquanshuzhi'
#数据库存储位置,密码以及防乱码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234567@localhost:3306/second_hand_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

#定义user及相应数据库
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique = True, nullable = False)
    pwd = db.Column(db.String(200), nullable = False)

#定义Goods类以及相应数据库,包含卖家,外键,关系,图片上传
class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),nullable = False)
    price = db.Column(db.Integer,nullable = False )
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    seller = db.relationship('User', backref=db.backref('goods', lazy=True))
    status = db.Column(db.String(20),default='on_sale')
    image_filename = db.Column(db.String(100),nullable=True)

#定义Order类以及相应数据库，包含外键等
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer,db.ForeignKey('goods.id'),nullable = False)
    buyer_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    price = db.Column(db.Float)

with app.app_context():
    db.create_all()


@app.route('/')
def index_page():
    #所有商品倒序方式排列展示(desc)
    all_goods = Goods.query.order_by(Goods.id.desc()).all()
    return render_template ('index.html',goods= all_goods)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pwd = request.form.get('pwd')
        if len(phone) != 11 or phone.isdigit():
            return "请输入11位纯数字,<a href='/register'>重新注册</a >"
        #从User数据库进行手机号查重
        #SELECT * FROM user WHERE phone = : phone LIMIT 1:
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            return "该手机号已注册,<a href='login '>去登录</a >"
        #哈希加密
        hash_pwd = generate_password_hash(pwd)
        new_user = User(phone=phone, pwd=hash_pwd)
        #数据库赋值给Session,Session赋值给session,最后进行try,若是没问题,add存储进session。
        Session = sessionmaker(bind=db.engine)
        session = Session()
        
        try:
            session.add(new_user)
            session.commit()
            return redirect('/login')
        #遇上意外情况数据回滚,保证数据的一致性
        except Exception as e:
            session.rollback()
            return "注册失败，请稍后再试"
        #释放资源,否则加重数据库的负担或导致数据过多后导致程序崩溃
        finally:
            session.close()
            
    return render_template('register.html')

@app.route('/login',methods = ['GET','POST'])
def login_page():
    #数据传输方式判断
    if request.method == 'POST':
        phone = request.form.get('phone')
        pwd = request.form.get('pwd')
        #User里面去查询
        user = User.query.filter_by(phone=phone).first()
        #用户手机号和密码核验
        if user and check_password_hash(user.pwd,pwd):
            #用session来确认用户登录态
            session['user_id'] = user.id
            session['phone'] = user.phone
            return redirect('/')
        else:
            return "手机号或密码不对！<a href='/login'>重新登录</a >"
    return render_template('login.html')

@app.route('/logout')
def logout():
    #清除用户登录态
    session.clear()
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    #判断用户登录态
    if 'user_id' not in session:
        return "请先登录！<a href='login'>去登录</a >"
        
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        #查重
        exist_goods = Goods.query.filter_by(name=name, seller_id=session['user_id']).first()
        if exist_goods:
            return "你已经上架过同名商品了！<a href='/index'>返回首页</a >"
        #接收前端文件使用files
        img = request.files.get('image')
        filename = None   
        if img and img.filename != '':
            #用python原生态代码进行数据切分，并用[1]来得到文件后缀名称
            ext = os.path.splitext(img.filename)[1]
            #判断文件格式是否是.jpg', '.jpeg', '.png', '.gif'
            if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
                return "只允许上传 jpg/png/gif 格式的图片！<a href='/upload'>返回</a >"
            #uuid随机乱码重命名，保障图片的唯一性
            filename = str(uuid.uuid4()) + ext
            #图片存储地方,后台'static', 'uploads', filename中
            save_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
            img.save(save_path)
        new_goods = Goods(name=name, price=float(price), seller_id=session['user_id'],image_filename=filename)
        db.session.add(new_goods)
        db.session.commit()
        
        return redirect('/')
    return render_template('upload.html')


@app.route('/buy/<int:goods_id>',methods = ['POST'])
def buy_page(goods_id):
    if 'user_id' not in session:
        return  "请先登录，<a href='/login'>去登录</a >"
    #使用商品唯一id进行查询
    goods = Goods.query.get(goods_id)
    if not goods:
        return"商品不存在,<a href='/'>返回主页</a >"
    #运用关系直接得到卖家id是否与登录id是同一人
    if goods.seller_id == session['user_id']:
        return"不能购买自己的商品,<a href='/'>返回主页</a >"
    upload_rows = Goods.query.filter_by(id = goods_id,status = 'on_sale').update({'status':'sold'})
    if upload_rows == 0:
        db.session.rollback()
        return "手慢了，商品已经被抢走了,<a href='/'>返回主页</a >"
    new_order = Order(buyer_id = session['user_id'], goods_id = goods.id, price = goods.price)
    db.session.add(new_order)
    goods.status = 'sold'
    db.session.commit()
    return"购买成功,<a href='/'>返回主页</a >"



@app.route('/delete/<int:goods_id>', methods=['POST'])
def remove_page(goods_id):
    if 'user_id' not in session:
        return "请先登录!<a href='login'>去登录</a >"
    goods = Goods.query.get(goods_id)
    if not goods:
        return"商品不存在,<a href='/upload'>去发布</a >"
    if goods.seller_id != session['user_id']:
        return"您无权删除他人商品,<a href='/upload'>去发布</a >"
    db.session.delete(goods)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
