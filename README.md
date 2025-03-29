# 桌宠“yxdd”

yxdd是一个使用Python编写的桌宠程序，使用DeepSeek+Kimi+Copilot辅助制作。

欲编译，请先执行
```
pip install pillow pystray pywin32
```

切记在assets中，将桌宠图片保存为“yxd.png”，将托盘图标保存为“tray.png”，并在“main.pyw”中对应修改“window_x”“window_y”“icon_x”“icon_y”这四个关键数值（单位：像素，分别为yxd.png的x、y；tray.png的x、y）。

使用Pyinstaller打包时，请注意路径！
```
pyinstaller --onefile --noconsole --add-data "assets;assets" --icon=logo.ico main.pyw
```
