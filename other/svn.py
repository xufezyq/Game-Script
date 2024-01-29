import subprocess
import time
import sys

file = open('output.txt', 'w')
original_stdout = sys.stdout
sys.stdout = file

# 记录开始时间
start_time = time.time()

# 执行svn update命令
svn_update_command = r'svn update D:\jx3_svn\Jx3Robot > D:\code\script\other\1.txt'
subprocess.check_call(svn_update_command, shell=True)

# 记录结束时间
end_time = time.time()

# 计算更新时长
update_duration = end_time - start_time

# 执行svn status命令，统计更新文件数量
svn_status_command = r'svn status -u D:\jx3_svn\Jx3Robot'
svn_status_output = subprocess.check_output(svn_status_command, shell=True).decode('utf-8')
updated_files = [line for line in svn_status_output.split('\n') if
                 line.strip() and not line.startswith('Status against revision')]
num_updated_files = len(updated_files)

print('更新时长:', update_duration, '秒')
print('更新文件数量:', num_updated_files)

sys.stdout = original_stdout
file.close()
