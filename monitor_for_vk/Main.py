# python3
# 所有脚本的调用入口

import sys
from opt_file_parser import OptFileParser


class MainMgr(object):

    def __init__(self):
        pass

    @staticmethod
    def parse_opt(opt_file_path):
        parser = OptFileParser(opt_file_path)
        parser.run()


if __name__ == '__main__':
    # python Main.py opt_file_path
    if len(sys.argv) != 2:
        print("Wrong Params!")
    MainMgr.parse_opt(sys.argv[1])
    print("Done!")
