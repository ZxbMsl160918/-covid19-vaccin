# 前言：仅供学习使用，请勿用作商业用途

背景：广州加油，广州加油，广州加油！由于广州疫情突然爆发，导致大家想打疫苗的欲望爆发式增长，目前可谓一苗难求。在此背景下，此程序诞生了。

### 

 ### 使用教程

   编辑 config/config.ini 文件，填写 cookie，stitches（预约第几针），date（预约日期）即可。

   下面介绍如何取得 cookie，请尽量使用**谷歌浏览器**（目前测试，谷歌、火狐均可）打开 http://test.h.plateform.umiaohealth.com/login.html?institutioncode=

   提前按 F12 切换到 Network，登陆成功后，在首页点击任意一个请求，能找到 cookie 就行。此处以请求首页的链接为例；

   ![get_cookie](https://raw.githubusercontent.com/ZxbMsl160918/img-repository/master/img/get_cookie.png)

将该 cookie 复制粘贴到配置文件就行，最后点击 start.bat 运行程序。
