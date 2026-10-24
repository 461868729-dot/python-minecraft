import os
import subprocess
import zipfile
import shutil

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
        fullzip = os.path.join(JAVA_DIR, name)
        if os.path.isfile(fullzip) and name.lower().endswith(".zip"):
            java_name_noext = os.path.splitext(name)[0]
            java_list.append((java_name_noext, fullzip))
    return java_list

def extract_java(zip_fullpath, target_folder_name):
    print("正在将Java解压到零时目录...")
    out_folder = os.path.join(BASE_DIR, target_folder_name)
    if os.path.exists(out_folder):
        shutil.rmtree(out_folder)
    os.makedirs(out_folder)
    with zipfile.ZipFile(zip_fullpath,"r") as zf:
        zf.extractall(out_folder)
    java_exe = os.path.join(out_folder, "bin", "java.exe")
    print("解压完成！")
    return out_folder, java_exe

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
    extracted_dir = None
    try:
        if not java_list:
            print("没有找到Java，请从仓库Tag中找到Java的文件（不要解压缩！），然后放置启动器根目录的Java文件夹中。")
            input()
            return
        if len(java_list) == 1:
            java_name, zip_path = java_list[0]
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
                        java_name, zip_path = java_list[num - 1]
                        break
                print("输入无效，重新选择")
            print("已选中Java: " + java_name)

        # 解压到脚本根目录，文件夹名就是zip去掉后缀
        extracted_dir, java_exe = extract_java(zip_path, java_name)

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
    finally:
        # 无论成功失败，都删除根目录解压出来的文件夹，原始zip不动
        if extracted_dir is not None and os.path.exists(extracted_dir):
            try:
                shutil.rmtree(extracted_dir)
            except Exception:
                pass
    input("按回车关闭...")

if __name__ == "__main__":
    main()
