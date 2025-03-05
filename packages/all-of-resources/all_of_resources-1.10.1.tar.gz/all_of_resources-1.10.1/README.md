# 📦 All Of Resources
一个工具可以从client.jar和.minecraft/assets文件夹提取minecraft所有资源的工具  
请勿分发使用这个程序提取出来的资源，这些资源仅用作资源包的开发，我不会对此承担任何责任

## 🛠️ 安装
1. 使用pip安装
    ```bash
    pip install all-of-resources
    ```
    运行
    ```bash
    # Flutter界面
    aor

    # Tk界面
    aortk
    ```

2. 针对Windows的二进制文件
   直接下载并解压Release的`all-of-resources_1.00_windows.7z`文件，然后运行`aor.exe`  
   如果Windows版本太老，也可以使用`aortk.exe`的旧界面

## 🖼️ 截图
tkinter前段：
![](./screenshot1.png)
![](./screenshot2.png)

## 📓 更新日志
### 1.10.1
- 手机的图标有点不对劲 (flet默认图标)... 我给他修了
- 现在手机端分离了apk，armabi和arm64两个架构使用了不同的安装包，减小了apk的大小

### 1.10
- 分离了前后端
- 添加了flet前段以支持手机
- 移除了Herobrine

### 1.00
- 第一个版本