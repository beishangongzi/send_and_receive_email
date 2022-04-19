#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
import os
import poplib
import time
from email.header import decode_header
from email.parser import Parser
from optparse import OptionParser

import config3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def decode_str(s):  # 字符编码转换
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def get_att(msg, **kwargs):
    import email
    attachment_files = []
    for part in msg.walk():
        file_name = part.get_filename()  # 获取附件名称类型
        sender, date = get_sender_and_date(msg)
        if file_name:
            h = email.header.Header(file_name)
            dh = email.header.decode_header(h)  # 对附件名称进行解码
            filename = dh[0][0]
            if dh[0][1]:
                filename = decode_str(str(filename, dh[0][1]))  # 将附件名称可读化
            data = part.get_payload(decode=True)  # 下载附件
            try:
                destination = os.path.join(kwargs["destination"], file_name)
            except:
                destination = os.path.join(sender, date, "att_" + file_name)
            att_file = open(destination, 'wb')  # 在指定目录下创建文件，注意二进制文件需要用wb模式打开
            attachment_files.append(filename)
            att_file.write(data)
            att_file.close()
            logging.info(f"download attachment {filename} to {destination}")
    return attachment_files


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def get_sender_and_date(msg):
    sender = msg["From"].split("@")[0]
    d = msg["Date"].split("+")[0].strip()
    date = datetime.datetime.strptime(d, "%a, %d %b %Y %H:%M:%S")
    date = datetime.datetime.isoformat(date).replace(":", "-")
    return sender, date


def get_msg(msg):
    parts = msg.get_payload()
    message = parts[0]
    content = message.get_payload(decode=True)
    charset = guess_charset(message)
    content = content.decode(charset)
    sender, date = get_sender_and_date(msg)
    file_name = "message.txt"
    file_path = os.path.join(sender, date)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(os.path.join(file_path, file_name), "w") as f:
        f.write(content)
    logging.info("download the context")


def receive(host, port, receiver, password, number, **kwargs):
    server = poplib.POP3_SSL(host=host, port=port)
    server.user(receiver)
    server.pass_(password)
    logging.info('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    index = len(mails)
    if number == "all":
        end = 0
    else:
        end = index - eval(number)
    for i in range(index, end, -1):
        logging.info(f"receive the {index - i + 1}th email")
        # for i in range(1, index+1, 1):
        # 倒序遍历邮件
        resp, lines, octets = server.retr(i)
        # lines存储了邮件的原始文本的每一行,
        # 邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        # 解析邮件:
        msg = Parser().parsestr(msg_content)
        # 获取邮件时间
        date1 = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')  # 格式化收件时间
        date2 = time.strftime("%Y%m%d", date1)  # 邮件时间格式转换
        # if (date2 < '20180306') | (date2 > '20180314'):
        #     continue
        # f_list = get_att(msg)  # 获取附件
        get_msg(msg)
        # print_info(msg)
        get_att(msg, **kwargs)
    server.quit()


def main():
    host = config.RECEIVE_EMAIL_HOST
    port = config.RECEIVE_EMAIL_PORT
    password = config.RECEIVE_EMAIL_HOST_PASSWORD
    receiver = config.RECEIVE_EMAIL_HOST_USER
    number = "1"
    kwargs = {}
    parser = OptionParser(add_help_option=True)
    parser.add_option("-H", "--host", dest="host", default=host, type="str",
                      help="host of the receiver")
    parser.add_option("-P", "--port", dest="port", default=port, type="int",
                      help="port of the receiver")
    parser.add_option("-s", "--receiver", dest="receiver", default=receiver, type="str",
                      help="who receive the email")
    parser.add_option("-p", "--password", dest="password", default=password, type="str",
                      help="the password to the receiver's server")
    parser.add_option("-n", "--number", dest="number", type="str", default=number,
                      help="how many that you want to receive")
    parser.add_option("-d", "--destination", dest="destination", type="str",
                      help="destination that you want to save you attachment")
    (options, args) = parser.parse_args()
    if options.destination is not None and eval(options.number) != 1:
        logging.warning("If a path is specified, it is recommended to receive only one email")
    if options.destination is not None:
        kwargs.update({"destination": options.destination})
    receive(host=options.host,
            port=options.port,
            receiver=options.receiver,
            password=options.password,
            number=options.number,
            **kwargs)


if __name__ == '__main__':
    main()
