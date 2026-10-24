import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAVA_DIR = os.path.join(BASE_DIR, "Java")
COMMON_LWJGL_DIR = os.path.join(BASE_DIR, "lwjgl")

# 版本 -> 主类映射表
VERSION_MAINCLASS = {
    "rd-161348": "com.mojang.minecraft.RubyDung",
    "rd-20090515": "com.mojang.minecraft.RubyDung",
    "1.0":"net.minecraft.client.Minecraft",
    "1.3":"net.minecraft.client.Minecraft",
    "1.4":"net.minecraft.client.Minecraft",
    "1.5":"net.minecraft.client.Minecraft"
}

# 默认主类（不在上面表里的版本用这个）
DEFAULT_MAINCLASS = "com.mojang.rubydung.RubyDung"


def find_all_java():
    java_list = []
    if not os.path.isdir(JAVA_DIR):
        return java_list
    for name in os.listdir(JAVA_DIR):
        exe = os.path.join(JAVA_DIR, name, "bin", "java.exe")
        if os.path.isfile(exe):
            java_list.append((name, exe))
    return java_list


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


def collect_common_jars():
    jars = []
    if os.path.isdir(COMMON_LWJGL_DIR):
        for fn in os.listdir(COMMON_LWJGL_DIR):
            if fn.lower().endswith(".jar"):
                jars.append(os.path.join(COMMON_LWJGL_DIR, fn))
    return jars


def main():
    java_list = find_all_java()
    if not java_list:
        print("没有找到Java")
        input()
        return
    if len(java_list) == 1:
        java_name, java_exe = java_list[0]
        print("自动选择Java: " + java_name)
    else:
        print("可用Java版本")
        for idx, (jname, jpath) in enumerate(java_list):
            print("[" + str(idx + 1) + "] " + jname)
        while True:
            sel_java = input("请选择Java编号：").strip()
            if sel_java.isdigit():
                num = int(sel_java)
                if 1 <= num <= len(java_list):
                    java_name, java_exe = java_list[num - 1]
                    break
            print("输入无效，重新选择")
        print("已选中Java: " + java_name)

    versions = list_rd_versions()
    if not versions:
        print("没有找到minecraft版本jar")
        input()
        return
    print("可用minecraft版本")
    for v in versions:
        print(v)
    sel = input("请选择minecraft版本：").strip()
    if sel not in versions:
        print("版本不存在")
        input()
        return

    game_jar = os.path.join(BASE_DIR, sel + ".jar")
    natives_dir = os.path.join(BASE_DIR, sel)
    if not os.path.isdir(natives_dir):
        print("缺少natives文件夹: " + natives_dir)
        input()
        return

    # 从字典取主类，没有匹配就用默认
    main_class = VERSION_MAINCLASS.get(sel, DEFAULT_MAINCLASS)
    print(f"识别主类: {main_class}")

    common_jars = collect_common_jars()
    classpath_parts = [game_jar] + common_jars
    classpath = ";".join(classpath_parts)

    cmd = [
        java_exe,
        "-Djava.library.path=" + natives_dir,
        "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=true",
        "-cp", classpath,
        main_class
    ]
    print("Natives目录：" + natives_dir)
    print("Classpath：" + classpath)
    print("启动游戏")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:")
    print(proc.stdout)
    print("STDERR:")
    print(proc.stderr)
    print("返回码：" + str(proc.returncode))
    input("按回车关闭...")


if __name__ == "__main__":
    main()
