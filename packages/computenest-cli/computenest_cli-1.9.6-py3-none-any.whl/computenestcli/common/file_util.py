import os
import shutil
import sys

if sys.version_info >= (3, 10):
    from importlib import resources
else:
    import importlib_resources as resources

exclude_dirs = ['.git', '.idea', '.vscode', '.DS_Store', '__pycache__']


class FileUtil:
    def __init__(self):
        pass

    @staticmethod
    def remove_subdirectories(directories):
        if not directories:
            return set()
        # 将目录列表先排序，以便父目录出现在前面
        sorted_dirs = sorted(directories)

        # 储存父目录的集合
        filtered_dirs = set()

        for dir_path in sorted_dirs:
            # 检查当前目录是否是已经在集合中的任何父目录的子目录
            if not any(dir_path.startswith(parent_dir + '/') for parent_dir in filtered_dirs):
                filtered_dirs.add(dir_path)

        return filtered_dirs

    @staticmethod
    def copy_excluding_directory(src, dest, exclude_dir):
        # 创建目标目录
        if not os.path.exists(dest):
            os.makedirs(dest)

        if not os.path.exists(src):
            os.makedirs(os.path.join(dest, os.path.relpath(src, os.getcwd())), exist_ok=True)
            return

        # 对于是src_dir为命令执行的根目录情况，需要跳过部分文件
        if src == os.getcwd():
            for item in os.listdir(src):
                s_item = os.path.join(src, item)
                d_item = os.path.join(dest, item)
                # 跳过部分指定目录
                if item in exclude_dirs:
                    continue
                if os.path.isdir(s_item) and not os.path.commonpath([s_item]) == os.path.commonpath(
                        [s_item, exclude_dir]):
                    FileUtil.copy_tree_overwrite(s_item, d_item)
                    continue
                elif os.path.isfile(s_item):
                    shutil.copy2(s_item, d_item)
            return

        # 对于其他情况，直接复制
        dest = os.path.join(dest, os.path.relpath(src, os.getcwd()))

        if not os.path.exists(src) or not os.listdir(src):
            os.makedirs(dest, exist_ok=True)
            return

        if os.path.isdir(src):
            FileUtil.copy_tree_overwrite(src, dest)
        else:
            shutil.copy2(src, dest)

    @staticmethod
    def copy_from_package(src_package, src_name, dst_directory):
        with resources.path(src_package, src_name) as src_path:
            if src_path.is_dir():
                FileUtil.copy_tree_overwrite(src_path, dst_directory)
            else:
                shutil.copy2(src_path, dst_directory / src_name)

    @staticmethod
    def write_to_file(file_path, content):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory {directory} created.")
        try:
            with open(file_path, 'w+') as file:
                file.write(content)
            print(f"Content successfully written to {file_path}")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def delete_path(target_path):
        """
        删除指定路径下的文件或目录。

        :param target_path: 需要删除的文件或目录路径。
        """
        try:
            if os.path.isdir(target_path):
                # 如果目标路径是目录，删除整个目录及其所有内容
                shutil.rmtree(target_path)
                print(f"目录删除成功: {target_path}")
            elif os.path.isfile(target_path):
                # 如果目标路径是文件，删除文件
                os.remove(target_path)
                print(f"文件删除成功: {target_path}")
            else:
                print(f"路径不存在或不是常规文件/目录: {target_path}")
        except Exception as e:
            print(f"删除目标时出现错误: {e}")

    # 复制目录树，兼容python3.8之前的版本
    @staticmethod
    def copy_tree_overwrite(src, dst):
        # 检查目标目录是否存在
        if os.path.exists(dst):
            # 删除目标目录以清空旧内容
            shutil.rmtree(dst)

        # 复制目录树
        shutil.copytree(src, dst)
