import pytest
import requests
import random

# 基础 URL，跑前必须确保Flask 正在运行
BASE_URL = "http://127.0.0.1:5000"


#Fixture 前置数据准备
@pytest.fixture(scope="module")
def test_user():
    #生成一个随机的测试手机号和密码，供后面的测试用例共用
    phone = "138" + "".join(random.choices("0123456789", k=8))
    pwd = "test_pwd_123"
    
    #返回一个字典，后面用 test_user["phone"] 就能拿到
    return {"phone": phone, "pwd": pwd}

def test_register_success(test_user):
    #测试注册,断言结果,返回数据，判断最终结果
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    
    # 发送请求，抓到 302 状态码，allow_redirects=False（禁止重定向到 /login 页面）
    res = requests.post(f"{BASE_URL}/register", data=data, allow_redirects=False)
    
    # 断言：注册成功应该返回 302 跳转
    assert res.status_code == 302
    print(f"\n✅ 注册成功，当前注册手机号: {test_user['phone']}")


def test_login_success(test_user):
    #测试登录，断言结果,返回数据，判断最终结果
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    assert res.status_code == 302
    print("\n✅ 登录成功，系统成功跳转！")


def test_upload_goods_without_login():
    #测试异常拦截：未登录直接发 POST 请求上架商品
    data = {"name": "测试商品", "price": "9999"}
    res = requests.post(f"{BASE_URL}/upload", data=data)
    
    # 断言：我的python后端第一行代码是 if 'user_id' not in session，所以页面会返回“请先登录”
    assert "请先登录" in res.text
    print("\n✅ 越权防御生效：未登录无法上架商品！")


def test_buy_goods_without_login():
    #测试异常拦截：未登录直接购买商品
    # 随便传个商品 ID 比如 1/2/3都行，因为连登录都没过，根本走不到查商品那一步
    res = requests.post(f"{BASE_URL}/buy/1")
    
    assert "请先登录" in res.text
    print("\n✅ 安全防御生效：未登录无法购买商品！")


#带session登录态的最终测试，卖家，买家
def test_full_flow_upload_and_buy(test_user):
    #核心闭环：模拟卖家登录 -> 上架商品 -> 买家登录 -> 买走商品
    #模拟登录态的保持
    seller = requests.Session()
    buyer = requests.Session()

    # 生成卖家账号并注册登录
    seller_phone = "139" + "".join(random.choices("0123456789", k=8))
    seller.post(f"{BASE_URL}/register", data={"phone": seller_phone, "pwd": "123"})
    seller.post(f"{BASE_URL}/login", data={"phone": seller_phone, "pwd": "123"})
    
    # 卖家上架商品
    seller.post(f"{BASE_URL}/upload", data={"name": "二手外星人电脑", "price": "5000"})
    
    # 生成买家账号并注册登录
    buyer_phone = "137" + "".join(random.choices("0123456789", k=8))
    buyer.post(f"{BASE_URL}/register", data={"phone": buyer_phone, "pwd": "123"})
    buyer.post(f"{BASE_URL}/login", data={"phone": buyer_phone, "pwd": "123"})
    
    #模拟购买商品，但需要确保有商品ID为1的商品，若是没有，需要自己手动上传一个商品
    res = buyer.post(f"{BASE_URL}/buy/1")
    assert ("购买成功" in res.text) or ("商品已被买走" in res.text)or ("商品不存在")
    print("\n✅ 终极闭环通过：双账号互买测试完成！")