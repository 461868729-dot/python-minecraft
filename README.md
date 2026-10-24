# Python版Minecraft
本项目为Minecraft3D的简和体中文版本。


## PYMC启动器
### PYMC启动器支持启动Minecraft和rd版本，launch.py是主程序。
这些代码决定能够启动哪些版本：
```python
def list_rd_versions():
    versions = []
    for f in os.listdir(BASE_DIR):
        if f.lower().endswith(".jar") and f.startswith("rd-"):
            ver = os.path.splitext(f)[0]
            versions.append(ver)
        if f.lower().endswith(".jar") and f.startswith("1."):
            ver = os.path.splitext(f)[0]
            versions.append(ver)
    return sorted(versions)
```
通过复制if语句来实现，f.startswith的括号中就是允许的前缀。
还需要根据主类填写VERSION_MAINCLASS字典，比如：
`"1.0":"net.minecraft.client.Minecraft"`
这个指定了Minecraft1.0的启动主类是`net.minecraft.client.Minecraft`。

## PYMC游戏
### 这是基于ursina的3DMinecraft版本，根据`user.txt`和`level.txt`和`level1.txt`和`level2.txt`完成，如果目录下没有这些文件，会自动生成。
修改`SIZE`变量可以修改一次生成的方块数，越多越卡。