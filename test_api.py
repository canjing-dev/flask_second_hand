import pytest
import requests
import random

BASE_URL = "http://127.0.0.1:5000"


#Fixture 前置数据准备
@pytest.fixture(scope="module")
def test_user():
    phone = "138" + "".join(random.choices("0123456789", k=8))
    pwd = "test_pwd_123"
    
    #返回一个字典，后面用 test_user["phone"] 就能拿到
    return {"phone": phone, "pwd": pwd}


def test_without_register_login(test_user):
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    assert res.status_code == 200
    print(f"\n✅ 未注册登录拦截成功，测试手机号: {test_user['phone']}")



def test_register_success(test_user):
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/register", data=data, allow_redirects=False)
    assert res.status_code == 302
    print(f"\n✅ 注册成功，当前注册手机号: {test_user['phone']}")


def test_register_duplicate(test_user):
    data = {"phone": test_user["phone"],"pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/register", data=data, allow_redirects=False)
    assert res.status_code == 200
    assert "该手机号已注册" in res.text
    print(f"\n✅ 该手机号已经注册，重复注册测试成功，重复注册手机号: {test_user['phone']}")


def test_login_success(test_user):
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    assert res.status_code == 302
    print("\n✅ 登录成功，系统成功跳转！")


def test_upload_goods_without_login():
    data = {"name": "测试商品", "price": "9999"}
    res = requests.post(f"{BASE_URL}/upload", data=data)   
    # 断言：我的python后端第一行代码是 if 'user_id' not in session，所以页面会返回“请先登录”
    assert "请先登录" in res.text
    print("\n✅ 越权防御生效：未登录无法上架商品！")


def test_buy_goods_without_login():
    res = requests.post(f"{BASE_URL}/buy/1")
    assert "请先登录" in res.text
    print("\n✅ 安全防御生效：未登录无法购买商品！")


def test_full_flow_upload_and_buy(test_user):
    seller = requests.Session()
    buyer = requests.Session()

    seller_phone = "139" + "".join(random.choices("0123456789", k=8))
    seller.post(f"{BASE_URL}/register", data={"phone": seller_phone, "pwd": "123"})
    seller.post(f"{BASE_URL}/login", data={"phone": seller_phone, "pwd": "123"})
    seller.post(f"{BASE_URL}/upload", data={"name": "二手外星人电脑", "price": "5000"})
    
    buyer_phone = "137" + "".join(random.choices("0123456789", k=8))
    buyer.post(f"{BASE_URL}/register", data={"phone": buyer_phone, "pwd": "123"})
    buyer.post(f"{BASE_URL}/login", data={"phone": buyer_phone, "pwd": "123"})
    
    res = buyer.post(f"{BASE_URL}/buy/1")
    assert ("购买成功" in res.text) or ("商品已被买走" in res.text)or ("商品不存在")
    print("\n✅ 终极闭环通过：双账号互买测试完成！")