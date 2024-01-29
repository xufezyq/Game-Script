import msvcrt
import subprocess
from datetime import datetime


def svn_cleanup_update(path):
    try:
        # 执行 cleanup 命令
        print("执行 cleanup 命令")
        cleanup_command = ['svn', 'cleanup', path]
        subprocess.run(cleanup_command, check=True)

        print("执行 update 命令")
        # 执行 update 命令
        update_command = ['svn', 'update', path]
        subprocess.run(update_command, check=True)
        return True

    except subprocess.CalledProcessError as e:
        print("出现错误：", e)
        return False


if __name__ == '__main__':
    begin_time = datetime.now()
    # 指定要操作的 SVN 仓库路径
    repository_path = r'E:\sword3-products\trunk\client'
    # 调用函数执行 cleanup 和 update
    svnRes = False
    while not svnRes:
        svnRes = svn_cleanup_update(repository_path)
    current_time = datetime.now()
    print(f"完成时间：{current_time}，总计耗时：{current_time-begin_time}")
    print('done!!!')
    msvcrt.getch()
