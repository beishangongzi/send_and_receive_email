# 收发邮件

## 发邮件
1. `python send.py -S test -a a.txt -a b.txt -m "hello this is the context"`
   
    这将会发送标题是text,内容是‘hello this is the context’,附件是a.txt b.txt的邮箱。
    默认的收件人和发件人在配置文件读取。

## 收邮件
1. `python receive.py -n 1`
   
    收取最近的一封邮件
2. `python receive.py -n all`
   
    收取所有的邮件
3. `python receive.py -n 1 -d your/path`
   
    将附件下载到指定路径

## 帮助文档

查看帮助文档`python send.py -h` 或者 `python send.py --help`