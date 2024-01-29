import msvcrt
import subprocess
import sys
import time
from datetime import datetime


def svn_cleanup_update(path, fwrite):
    try:
        # 执行 cleanup 命令
        fwrite.write("执行 cleanup 命令" + f' Time: {datetime.now()}\n')
        cleanup_command = ['svn', 'cleanup', path]
        subprocess.run(cleanup_command, check=True)

        # 执行 update 命令
        fwrite.write("执行 update 命令" + f' Time: {datetime.now()}\n')
        update_command = ['svn', 'update', '--accept', 'theirs-full', path]
        subprocess.run(update_command, check=True, stdout=fwrite)

        # 执行 cleanup 命令
        fwrite.write("执行 update --vacuum-pristines 命令" + f' Time: {datetime.now()}\n')
        pristine = ['svn', 'cleanup', '--vacuum-pristines', path]
        subprocess.run(pristine, check=True, stdout=fwrite)

        return True

    except subprocess.CalledProcessError as e:
        now_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        print(f"{now_time}-出现错误：", e)
        return False


if __name__ == '__main__':
    begin_time = datetime.now()
    # 指定要操作的 SVN 仓库路径
    repository_path = r'E:\sword3-products\trunk\client'
    # 指定保存的输出文件路径
    outfile_name = begin_time.strftime('%Y%m%d-%H%M%S') + '.txt'
    output_path = rf'E:\log\{outfile_name}'
    # 修改标准输出
    file = open(output_path, 'w')
    sys.stdout = file
    # 调用函数执行 cleanup 和 update
    svnRes = False
    while not svnRes:
        svnRes = svn_cleanup_update(repository_path, file)
        time.sleep(5)
    current_time = datetime.now()
    print(f"完成时间：{current_time}，总计耗时：{current_time - begin_time}")
    print('done!!!')
    file.close()
