import os
import subprocess
import re
import shutil
import sys


def format_time_for_filename(time_str):
    """将时间格式如 00:00-03:14:59 转换为 00_00-03_14_59 用于文件名"""
    return time_str.replace(':', '_')


def is_valid_time_format(time_str):
    """检查时间段格式是否正确"""
    return re.match(r'^\d{2}:\d{2}(:\d{2})?-\d{2}:\d{2}(:\d{2})?$', time_str) is not None


def check_ffmpeg():
    """检查ffmpeg是否已安装"""
    if shutil.which('ffmpeg') is None:
        print("错误：ffmpeg 未安装，请先安装 ffmpeg")
        return False
    return True


def get_audio_files(directory):
    """获取目录中的音频文件列表"""
    audio_files = []
    if not os.path.exists(directory):
        print(f"错误：{directory} 目录不存在")
        return audio_files

    for file in os.listdir(directory):
        if file.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')):
            audio_files.append(file)

    return audio_files


def get_valid_directory(prompt, default):
    """获取有效的目录路径"""
    while True:
        directory = input(f"{prompt} [{default}]: ") or default

        # 如果是相对路径，则转换为绝对路径并显示
        if not os.path.isabs(directory):
            abs_path = os.path.abspath(directory)
            print(f"使用相对路径，绝对路径为: {abs_path}")
        else:
            abs_path = directory

        if not os.path.exists(abs_path):
            create = input(f"目录 {abs_path} 不存在，是否创建? (y/n): ")
            if create.lower() == 'y':
                try:
                    os.makedirs(abs_path)
                    print(f"已创建目录: {abs_path}")
                    return directory
                except Exception as e:
                    print(f"创建目录出错: {e}")
            else:
                print("请输入有效的目录路径")
        else:
            return directory


def get_valid_time_segment():
    """获取有效的时间段"""
    while True:
        time_segment = input("请输入要截取的时间段 (格式如 00:00-03:14:59): ")
        if is_valid_time_format(time_segment):
            return time_segment
        else:
            print("错误：时间格式不正确，应为 HH:MM-HH:MM 或 HH:MM:SS-HH:MM:SS")


def cut_audio(input_path, output_path, start_time, end_time):
    """使用ffmpeg截取音频"""
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-ss', start_time,
        '-to', end_time,
        '-y',  # 如果输出文件已存在则覆盖
        output_path
    ]

    try:
        # 使用binary模式运行命令，避免编码问题
        result = subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
        return True, None
    except subprocess.CalledProcessError as e:
        # 安全地解码错误信息
        try:
            error_msg = e.stderr.decode('utf-8', errors='replace')
        except:
            error_msg = "无法解码错误信息"
        return False, error_msg


def display_multiple_file_menu(files, header="请选择文件"):
    """显示文件选择菜单，允许选择多个文件"""
    if not files:
        print("没有找到音频文件")
        return None

    print(f"\n{header}:")
    print("0. 选择所有文件")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    print("\n提示: 输入多个数字(用逗号分隔)可选择多个文件，例如: 1,3,5")
    print("      输入范围可快速选择连续文件，例如: 2-5 会选择2,3,4,5号文件")

    while True:
        try:
            choice = input("请输入文件编号 (0 代表所有文件): ").strip()

            # 选择所有文件
            if choice == "0":
                return files

            # 处理范围输入，如"2-5"
            if "-" in choice:
                start, end = map(int, choice.split("-"))
                if 1 <= start <= len(files) and 1 <= end <= len(files):
                    return [files[i - 1] for i in range(start, end + 1)]
                else:
                    print(f"请输入有效范围 (1-{len(files)})")
                    continue

            # 处理多个选择，如"1,3,5"
            if "," in choice:
                indices = [int(x.strip()) for x in choice.split(",")]
                if all(1 <= idx <= len(files) for idx in indices):
                    return [files[idx - 1] for idx in indices]
                else:
                    print(f"请输入有效的文件编号 (1-{len(files)})")
                    continue

            # 单个选择
            idx = int(choice)
            if 1 <= idx <= len(files):
                return [files[idx - 1]]
            else:
                print(f"请输入 1 到 {len(files)} 之间的数字")

        except ValueError:
            print("请输入有效的数字")


def merge_audio_files(raw_dir, output_dir, selected_files):
    """将多个音频文件拼接成一个文件"""
    if not selected_files or len(selected_files) < 2:
        print("至少需要选择两个文件才能进行拼接")
        return False

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        try:
            print(f"输出目录 {output_dir} 不存在，正在创建...")
            os.makedirs(output_dir)
            print(f"成功创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            print("请手动创建输出目录或选择其他目录")
            return False

    # 创建临时文件列表
    temp_file = "temp_file_list.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        for file in selected_files:
            input_path = os.path.join(raw_dir, file)
            f.write(f"file '{input_path}'\n")

    # 获取第一个文件的名称作为输出文件名前缀
    first_filename, extension = os.path.splitext(selected_files[0])
    output_filename = f"{first_filename}_merge{extension}"
    output_path = os.path.join(output_dir, output_filename)

    print(f"\n正在拼接 {len(selected_files)} 个音频文件...")
    print(f"文件将按以下顺序拼接:")
    for i, file in enumerate(selected_files, 1):
        print(f"{i}. {file}")

    # 构建ffmpeg命令
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', temp_file,
        '-c', 'copy',
        '-y',  # 如果输出文件已存在则覆盖
        output_path
    ]

    try:
        # 执行ffmpeg命令
        result = subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
        print(f"\n拼接成功! 输出文件: {output_path}")

        # 删除临时文件列表
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return True
    except subprocess.CalledProcessError as e:
        print("拼接过程中出错")
        try:
            error_msg = e.stderr.decode('utf-8', errors='replace')
            print("错误详情:")
            print(error_msg)
        except:
            print("无法解码错误信息")

        # 删除临时文件列表
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return False


def process_files(raw_dir, output_dir, selected_files, time_segment):
    """处理选定的文件"""
    if not selected_files:
        print("没有选择任何文件进行处理")
        return

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        try:
            print(f"输出目录 {output_dir} 不存在，正在创建...")
            os.makedirs(output_dir)
            print(f"成功创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            print("请手动创建输出目录或选择其他目录")
            return

    # 分割为开始和结束时间
    start_time, end_time = time_segment.split('-')

    # 格式化时间用于文件名
    filename_time = format_time_for_filename(time_segment)

    # 计数用于跟踪进度
    total_files = len(selected_files)
    successful_files = 0

    print(f"\n开始处理 {total_files} 个音频文件...")

    # 处理每个音频文件
    for index, audio_file in enumerate(selected_files, 1):
        input_path = os.path.join(raw_dir, audio_file)

        # 获取不带扩展名的文件名和扩展名
        filename, extension = os.path.splitext(audio_file)

        # 创建按照指定格式的输出文件名: "原文件名+00_00-03_14_59"
        output_filename = f"{filename}+{filename_time}{extension}"
        output_path = os.path.join(output_dir, output_filename)

        print(f"正在处理 [{index}/{total_files}]: {audio_file}...")

        # 再次确认输出目录存在（以防中途被删除）
        output_dir_path = os.path.dirname(output_path)
        if not os.path.exists(output_dir_path):
            try:
                os.makedirs(output_dir_path)
            except Exception as e:
                print(f"无法创建输出路径: {e}")
                continue

        success, error = cut_audio(input_path, output_path, start_time, end_time)

        if success:
            successful_files += 1
            print(f"成功导出到: {output_path}")
        else:
            print(f"处理 {audio_file} 时出错")
            if error:
                print("错误详情:")
                print(error)

                # 如果错误是关于目录不存在，给出更明确的提示
                if "No such file or directory" in str(error):
                    print(f"\n提示: 请确保输出目录 '{output_dir}' 已创建且有写入权限")
                    print(f"当前工作目录: {os.getcwd()}")
                    print(f"尝试手动创建目录: {output_dir}")

    print(f"\n处理完成: {successful_files}/{total_files} 个文件成功处理")
    return successful_files


def list_processed_files(output_dir):
    """列出已处理的文件"""
    print(f"\n{output_dir} 中的文件:")
    if not os.path.exists(output_dir):
        print("输出目录不存在")
        return

    files = os.listdir(output_dir)
    if not files:
        print("输出目录为空")
        return

    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")


def show_help():
    """显示帮助信息"""
    print("\n音频截取工具 - 使用说明:")
    print("1. 此工具用于批量截取音频文件的特定时间段")
    print("2. 时间段格式为 HH:MM-HH:MM 或 HH:MM:SS-HH:MM:SS")
    print("3. 例如：00:00-03:14:59 表示从0小时0分0秒截取到3小时14分59秒")
    print("4. 输出文件命名格式为：原文件名+00_00-03_14_59.扩展名")
    print("5. 工具使用系统安装的ffmpeg进行音频处理")
    print("6. 拼接功能会按照选择顺序将多个音频文件合并为一个文件")
    print("7. 拼接后的文件命名格式为：第一个文件名_merge.扩展名")
    print("\n注意事项:")
    print("- 可以使用相对路径或绝对路径")
    print("- 在Windows系统上，请确保路径格式正确")
    print("- 程序会自动检测ffmpeg是否安装")
    print("- 拼接功能要求所选文件格式兼容，否则可能导致拼接失败或音频异常")


def main_menu():
    """主菜单"""
    # 使用相对路径，更适合跨平台
    raw_dir = 'raw'
    output_dir = 'output'

    if not check_ffmpeg():
        input("按回车键退出...")
        return

    while True:
        print("\n" + "=" * 50)
        print("音频截取工具 - 主菜单")
        print("=" * 50)
        print(f"当前输入目录: {raw_dir}")
        print(f"当前输出目录: {output_dir}")
        print("1. 设置输入目录")
        print("2. 设置输出目录")
        print("3. 扫描并显示音频文件")
        print("4. 截取音频")
        print("5. 拼接音频")
        print("6. 查看已处理文件")
        print("7. 帮助")
        print("0. 退出程序")

        choice = input("\n请选择操作: ")

        if choice == "1":
            raw_dir = get_valid_directory("请输入音频文件目录路径", raw_dir)

        elif choice == "2":
            output_dir = get_valid_directory("请输入输出目录路径", output_dir)

        elif choice == "3":
            audio_files = get_audio_files(raw_dir)
            if audio_files:
                print(f"\n在 {raw_dir} 中找到 {len(audio_files)} 个音频文件:")
                for i, file in enumerate(audio_files, 1):
                    print(f"{i}. {file}")
            else:
                print(f"在 {raw_dir} 中没有找到音频文件")
                print("提示: 当前工作目录为 " + os.getcwd())
                print("如果文件位于其他位置，请使用选项1设置正确的目录")

        elif choice == "4":
            audio_files = get_audio_files(raw_dir)
            if not audio_files:
                print(f"在 {raw_dir} 中没有找到音频文件")
                continue

            selected_files = display_multiple_file_menu(audio_files, "请选择要截取的文件")
            if not selected_files:
                continue

            time_segment = get_valid_time_segment()
            process_files(raw_dir, output_dir, selected_files, time_segment)

            # 询问是否查看结果
            view_result = input("\n是否查看处理结果? (y/n): ")
            if view_result.lower() == 'y':
                list_processed_files(output_dir)

        elif choice == "5":
            audio_files = get_audio_files(raw_dir)
            if not audio_files:
                print(f"在 {raw_dir} 中没有找到音频文件")
                continue

            print("\n请选择要拼接的文件（按选择顺序进行拼接）")
            selected_files = display_multiple_file_menu(audio_files, "请选择要拼接的文件")
            if not selected_files or len(selected_files) < 2:
                print("至少需要选择两个文件才能进行拼接")
                continue

            merge_audio_files(raw_dir, output_dir, selected_files)

            # 询问是否查看结果
            view_result = input("\n是否查看处理结果? (y/n): ")
            if view_result.lower() == 'y':
                list_processed_files(output_dir)

        elif choice == "6":
            list_processed_files(output_dir)

        elif choice == "7":
            show_help()

        elif choice == "0":
            print("感谢使用音频截取工具，再见!")
            break

        else:
            print("无效的选择，请重新输入")


if __name__ == "__main__":
    main_menu()