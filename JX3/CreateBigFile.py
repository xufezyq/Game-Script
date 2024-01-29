import os


def create_large_file(file_path, size):
    chunk_size = 1024 * 1024 * 1024

    with open(file_path, 'wb') as f:
        while size > 0:
            if size >= chunk_size:
                f.write(b'\0' * chunk_size)
                size -= chunk_size
            else:
                f.write(b'\0' * size)
                break

def fill_disk_space(folder_path):
    disk_usage = 0
    file_count = 1
    file_prefix = 'large_file'

    while True:
        file_name = f'{file_prefix}_{file_count}.txt'
        file_path = os.path.join(folder_path, file_name)
        file_size = 100 * 1024 * 1024 * 1024  # 100GB

        try:
            create_large_file(file_path, file_size)
            disk_usage += file_size
            file_count += 1
            print(f"写入文件{file_path}，总计写入{file_size}Byte。")
        except OSError as e:
            print(f"磁盘空间已用尽，无法创建更多文件。总共创建了 {file_count - 1} 个文件。")
            break


if __name__ == '__main__':
    folder_path = r'G:\large file\files'
    os.makedirs(folder_path, exist_ok=True)

    fill_disk_space(folder_path)
