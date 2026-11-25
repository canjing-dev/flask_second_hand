<img width="1406" height="791" alt="pytest_pytest_auto_test3" src="https://github.com/user-attachments/assets/e5a84605-205b-4b0c-999c-97e9e018a064" />
这是一个基于Flask + MySQL独立开发的全栈Web项目。

技术栈:
后端:Python,Flask,SQLAlchemy。
数据库: MySQ。
测试: Pytest, Requests。
部署: Linux, Git。

核心功能：
用户注册(密码Hash加密)，登录(Session鉴权)。
商品上架(UUID防图片重名)，购买，防越权校验。
乐观锁防并发超卖机制。

自动化测试:
已实现 7 个核心接口自动化测试用例，涵盖正常流程与越权/重复注册/未注册登录等异常边界场景，运行结果全部 PASSED。
