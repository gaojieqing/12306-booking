# 12306-booking

## Mac selenium调试已经存在的Chrome浏览器

配置chrome

```bash
vi ~/.zshrc
```

在结尾添加

```bash
export PATH="/Applications/Google Chrome.app/Contents/MacOS:$PATH"
```

保存后退出，然后启动一个窗口

```bash
Google\ Chrome --remote-debugging-port=19222 --user-data-dir="~/ChromeProfile"
```

其中Google\ Chrome为一个命令，把chrome添加到环境变量就可以看到了
这里是指定chrome的端口19222，这段代码执行结束后也不会退出driver