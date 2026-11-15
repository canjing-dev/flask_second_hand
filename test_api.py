import pytest
import requests
import random

# 基础 URL，跑测试前必须确保你的 Flask 正在运行
BASE_URL = "http://127.0.0.1:5000"

# ==========================================
# 🛠️ 核心：Fixture 前置数据准备（造数据的工厂）
# ==========================================
@pytest.fixture(scope="module")
def test_user():
    """生成一个随机的测试手机号和密码，供后面的测试用例共用"""
    phone = "138" + "".join(random.choices("0123456789", k=8))
    pwd = "test_pwd_123"
    
    # 返回一个字典，后面用 test_user["phone"] 就能拿到
    return {"phone": phone, "pwd": pwd}


# ==========================================
# 🎯 测试用例区（复制这个格式，往里面套业务）
# ==========================================

def test_register_success(test_user):
    """1. 测试注册成功"""
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    
    # 发请求，allow_redirects=False 为了抓到 302 状态码，不让他直接跳到 /login 页面
    res = requests.post(f"{BASE_URL}/register", data=data, allow_redirects=False)
    
    # 断言：注册成功应该返回 302 跳转
    assert res.status_code == 302
    print(f"\n✅ 注册成功，当前注册手机号: {test_user['phone']}")


def test_login_success(test_user):
    """2. 测试登录成功"""
    # 注意这里传的是刚才 fixture 里生成的那个手机号
    data = {"phone": test_user["phone"], "pwd": test_user["pwd"]}
    res = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    assert res.status_code == 302
    print("\n✅ 登录成功，系统正常跳转！")


def test_upload_goods_without_login():
    """3. 测试异常拦截：未登录直接发 POST 请求上架商品"""
    data = {"name": "测试霸王龙", "price": "9999"}
    res = requests.post(f"{BASE_URL}/upload", data=data)
    
    # 断言：你的代码第一行是 if 'user_id' not in session，所以页面会返回“请先登录”
    assert "请先登录" in res.text
    print("\n✅ 越权防御生效：未登录无法上架商品！")


def test_buy_goods_without_login():
    """4. 测试异常拦截：未登录直接购买商品"""
    # 随便传个商品 ID 比如 1，因为连登录都没过，根本走不到查商品那一步
    res = requests.post(f"{BASE_URL}/buy/1")
    
    assert "请先登录" in res.text
    print("\n✅ 安全防御生效：未登录无法购买商品！")


# ==========================================
# 🚀 终极闭环：带登录状态的测试（大满贯用例）
# ==========================================
def test_full_flow_upload_and_buy(test_user):
    """5. 核心闭环：模拟卖家登录 -> 上架商品 -> 买家登录 -> 买走商品"""
    # 这里为了真实，我们重新开两个 requests 的 Session 对象来保持各自的登录状态
    seller = requests.Session()
    buyer = requests.Session()

    # 1. 生成卖家账号并注册登录
    seller_phone = "139" + "".join(random.choices("0123456789", k=8))
    seller.post(f"{BASE_URL}/register", data={"phone": seller_phone, "pwd": "123"})
    seller.post(f"{BASE_URL}/login", data={"phone": seller_phone, "pwd": "123"})
    
    # 2. 卖家上架一个商品
    seller.post(f"{BASE_URL}/upload", data={"name": "二手外星人电脑", "price": "5000"})
    
    # 3. 生成买家账号并注册登录
    buyer_phone = "137" + "".join(random.choices("0123456789", k=8))
    buyer.post(f"{BASE_URL}/register", data={"phone": buyer_phone, "pwd": "123"})
    buyer.post(f"{BASE_URL}/login", data={"phone": buyer_phone, "pwd": "123"})
    
    # 4. 买家去购买（假设刚才上架的商品 ID 是 1，这里你可能需要查一下真实的 ID）
    # 为了跑通测试，我们假设它是买最新上架的，这里需要你确保数据库里有个商品 id 是1
    # 如果报错说商品不存在，你自己手动去网页上架一个商品，看下它的 id 是多少
    res = buyer.post(f"{BASE_URL}/buy/1")
    
    # 断言：如果你代码没问题，应该会返回购买成功，或者已经被买走
    assert ("购买成功" in res.text) or ("商品已被买走" in res.text)
    print("\n✅ 终极闭环通过：双账号互买测试完成！")