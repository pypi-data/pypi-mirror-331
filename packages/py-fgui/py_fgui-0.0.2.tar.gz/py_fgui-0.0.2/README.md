# py-fgui(Python-FairyGUI)

在Python中实现的，对于FGUI项目进行解析的库。可以解析到元件的层级。

未引用任何第三方库，仅使用Python自带的库。

目前功能还比较简陋，但已经满足了自己的大部分需求，欢迎各位大佬提出建议和PR，一起完善这个小项目。

# 快速开始

可以通过pip来安装：`pip install py-fgui`

接下来就能拿到关键数据了：

``` python
from py_fgui import *

# 加载一个FGUI项目
fgui_file_path:str = r"D:\FGUIProject\FGUIProject.fairy"
project:FGUIProject = FGUIProject(fgui_file_path)

# 获取项目的主分支（目前仅支持）
branch:FGUIBranch = project.main_branch

# 获取该分支下所有包
package_list:list[FGUIPackage] = branch.package_list

# 获取某个名字的包
master_package:FGUIPackage = branch.get_package_by_name("master")

# 获取指定url对应的资源
component_url:str = "ui://pkgidandresid"
resource:FGUIResource = branch.get_resource_by_url(component_url)

# 获取一个组件资源内部的元件
obj_list:list[FGUIObject] = resource.object_list
test_obj:FGUIObject = obj_list[0]

# 获取对其他资源的引用关系，会返回有效的引用资源和无效的引用资源
# 包层级的引用（包括包内所有资源，以及资源内所有元件）
pkg_ref_list, pkg_invalid_ref_list = master_package.get_references()
# 资源层级的引用（包括资源内所有元件）
res_ref_list, res_invalid_ref_list = resource.get_references()
# 元件层级的引用
obj_ref_list, obj_invalid_ref_list = test_obj.get_references()

# 你也可以判断一个对应的资源文件是否真的存在
if resource.file_exists is False:
    print("资源文件不存在")
else:
    print("资源文件存在于：" + resource.full_path)
```

想把依赖关系可视化成网络图？ 试试这个：

``` python
import networkx as nx
from pyvis.network import Network

from py_fgui import *

fgui_file_path:str = r"D:\FGUIProject\FGUIProject.fairy"
project:FGUIProject = FGUIProject(fgui_file_path)
branch:FGUIBranch = project.main_branch

# 创建依赖关系的映射
network_map:dict[str,list[str]] = dict()

for package in branch.package_list:
    print(f"Package: {package.package_name}")
    package_name_set:set[str] = set()
    all_references, _ = package.get_references()
    for reference_url in all_references:
        reference_package_name:str = branch.get_package_by_id(reference_url.package_id).package_name
        package_name_set.add(reference_package_name)

    for package_name in package_name_set:
        print(f"    {package_name}")
        if package.package_name not in network_map:
            network_map[package.package_name] = []
        network_map[package.package_name].append(package_name)

# 绘制网络关系图
print("=" * 20)
G = nx.Graph()

for package_name in network_map:
    for reference_package_name in network_map[package_name]:
        G.add_edge(package_name, reference_package_name)

# 画图
nx.draw(G, with_labels=True)

nt = Network(
    height="100vh",
    width="100%",
    directed=True,
    notebook=False,  # 必须设置为 False 才能启用完整响应式支持
    bgcolor="#ffffff",
    cdn_resources="in_line"  # 内联资源，避免 CDN 依赖
)

nt.toggle_physics(False)

# 手动计算网格坐标
grid_spacing = 400  # 像素间距

# 按照引用数量排序，从多到少排序
nodes = list(G.nodes())
nodes.sort(key=lambda x: G.degree[x], reverse=True)


for idx, node in enumerate(nodes):
    row = idx // 20
    col = idx % 20
    x = col * grid_spacing
    y = row * grid_spacing
    nt.add_node(
        node,
        x=x,
        y=y,
        label=node,
        font={"size": 14, "color": "#333"},  # 优化标签可读性
        shape="box",  # 节点显示为方块
        color="#4CAF50"
    )

# 设置边的样式为直线
nt.set_edge_smooth('false')

# 添加边
for edge in G.edges():
    nt.add_edge(edge[0], edge[1], width=1.2, color="#666")

# 生成 HTML 并注入自定义 CSS
html_content = nt.generate_html()

# 插入响应式 CSS 样式
css_injection = """
<style>
  body { margin: 0; padding: 0; overflow: hidden; }
  #mynetwork { 
    width: 100vw !important; 
    height: 100vh !important;
  }
</style>
"""
html_content = html_content.replace("</head>", css_injection + "</head>")


with open("fgui_net.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Export network to fgui_net.html")
```