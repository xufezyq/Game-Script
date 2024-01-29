import os
import pandas as pd


class MergeResSpyTxt(object):
    def __init__(self, directory):
        self.directory = directory  # txt文件目录
        self.file_list = []  # 所有文件列表
        self.write_data_type_summary = []
        self.data_dict = {}
        self.output_path = os.path.join(self.directory, "AllResourceData.xlsx")
        self.summary_path = os.path.join(self.directory, "Summary.xlsx")
        self.DataManagerResources_path = os.path.join(self.directory, "DataManagerResources.xlsx")

        self.texture_total_size = 0
        self.texture_count = 0

        self.speedtree_mesh_size = 0
        self.speedtree_mesh_count = 0
        self.mesh_size = 0
        self.mesh_count = 0
        self.particle_mesh_size = 0
        self.particle_mesh_count = 0
        self.mesh_total_size = 0
        self.mesh_total_count = 0

        self.material_count = 0

        self.actor_count = 0

    def read_file(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 把文件路径添加到列表中
                self.file_list.append(file_path)
        # 存储数据

        for file in self.file_list:
            if '.txt' in file:
                file_name = os.path.basename(file)
                data = pd.read_csv(file, encoding='gbk', sep='\t')
                sheet_name = file_name[:file_name.find('_')]
                self.data_dict[sheet_name] = data

    def merge_DataManagerResources(self):
        data_type = {}
        data_type_summary = {}
        df = pd.read_excel(self.output_path, 'DataManagerResources')
        for _, row in df.iterrows():
            if row['Type'] not in data_type.keys():
                data_type[row['Type']] = [[row['Name'], row['Size'], row['RefCount']]]
                data_type_summary[row['Type']] = int(row['Size'])
            else:
                data_type[row['Type']].append([row['Name'], row['Size'], row['RefCount']])
                data_type_summary[row['Type']] += int(row['Size'])
        with pd.ExcelWriter(self.DataManagerResources_path) as writer:
            for key in data_type.keys():
                write_data_type = data_type[key]
                self.write_data_type_summary.append(
                    [key, len(write_data_type), data_type_summary[key] / 1024])
                df = pd.DataFrame(write_data_type, columns=['Name', 'Size', 'RefCount'])
                df.to_excel(writer, sheet_name=key, index=False)

    def merge_texture(self):
        df = pd.read_excel(self.output_path, sheet_name='ShaderTextureManagerResources')
        self.texture_count = df.shape[0]
        for _, row in df.iterrows():
            self.texture_total_size += int(row['Size(KB)']) / 1024

    def merge_mesh(self):
        df = pd.read_excel(self.output_path, sheet_name='MeshResources')
        self.mesh_total_count = df.shape[0]
        for _, row in df.iterrows():
            if row['mesh'] == 'mesh':
                self.mesh_count += 1
                self.mesh_size += row['Size'] / 1024 / 1024
            elif row['mesh'] == 'particle_mesh':
                self.particle_mesh_count += 1
                self.particle_mesh_size += int(row['Size']) / 1024 / 1024
            elif row['mesh'] == 'speedtree_mesh':
                self.speedtree_mesh_count += 1
                self.speedtree_mesh_size += int(row['Size']) / 1024 / 1024
        self.mesh_total_size = self.mesh_size + self.particle_mesh_size + self.speedtree_mesh_size

    def merge_material(self):
        df = pd.read_excel(self.output_path, sheet_name='MaterialInsPackData')
        self.material_count = df.shape[0]

    def merge_actor(self):
        df = pd.read_excel(self.output_path, sheet_name='InitSingleActor2023')
        self.actor_count = df.shape[0]

    def write_file(self):
        with pd.ExcelWriter(self.output_path) as writer:
            for key in self.data_dict.keys():
                self.data_dict[key].to_excel(writer, sheet_name=key, index=False)

    def write_summary_file(self):
        resource_data = [['texture', self.texture_count, self.texture_total_size],
                         ['Mesh', self.mesh_total_count, self.mesh_total_size],
                         ['material', self.material_count, 0],
                         ['Actor', self.actor_count, 0]]
        mesh_data = [['speedtree_mesh', self.speedtree_mesh_count, self.speedtree_mesh_size],
                     ['mesh', self.mesh_count, self.mesh_size],
                     ['particle_mesh', self.particle_mesh_count, self.particle_mesh_size]]
        with pd.ExcelWriter(self.summary_path) as writer:
            df = pd.DataFrame(resource_data, columns=['资源类型', '个数', '大小(MB)'])
            df.to_excel(writer, sheet_name='resource_data', index=False)
            df = pd.DataFrame(mesh_data, columns=['资源类型', '个数', '大小(MB)'])
            df.to_excel(writer, sheet_name='Mesh_data', index=False)
            df = pd.DataFrame(self.write_data_type_summary, columns=['Type', 'Count', 'Size(KB)'])
            df.to_excel(writer, sheet_name='DataManagerResources_summary', index=False)

    def run(self):
        self.read_file()
        self.write_file()
        self.merge_DataManagerResources()
        self.merge_texture()
        self.merge_mesh()
        self.merge_material()
        self.merge_actor()
        self.write_summary_file()


if __name__ == '__main__':
    xx = MergeResSpyTxt(r'D:\jx3_file\file_g_OpenFile\10.17 1024蓝天白云资源_关闭预加载')
    xx.run()
    print('done!!!')
