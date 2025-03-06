from __future__ import annotations

import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


# region FGUI常量定义
class FGUIExtensions:
    """
    FGUI的文件后缀。
    """

    PROJECT: str = ".fairy"
    """
    fgui项目文件后缀。
    """

    XML: str = ".xml"
    """
    fgui组件文件、包资源文件的后缀。
    """


class FGUIFileName:
    """
    FGUI项目中的文件名称。
    """

    PACKAGE_XML: str = "package.xml"
    """
    fgui项目中的`package.xml`文件名称。
    该文件存放了包的信息。
    """

    PACKAGE_BRANCH_XML: str = "package_branch.xml"
    """
    fgui项目中的`package_branch.xml`文件名称。
    该文件存放了分支包的信息。
    """


class FGUIFolderName:
    """
    FGUI项目中的文件夹名称。
    """

    ASSETS: str = "assets"
    """
    fgui项目中的`assets`文件夹名称。
    该文件夹下存放了所有的包，每个包都是一个文件夹。
    """

    ASSETS_BRANCH_PREFIX: str = "assets_"
    """
    fgui项目中的`assets`文件夹下的分支包的前缀。
    前缀后的部分是分支的名称。
    """

    SETTINGS: str = "settings"
    """
    fgui项目中的`settings`文件夹名称。
    该文件夹下存放了项目的配置文件。
    """

    OBJS: str = "objs"
    """
    fgui项目中的`.objs`文件夹名称
    该文件夹下存放了项目中一些中间文件，例如部分的设置和界面中元件的显隐状态。
    """

    PLUGINS: str = "plugins"
    """
    fgui项目中的`plugins`文件夹名称。
    该文件夹下存放了项目中的插件，每个插件都是一个文件夹。
    """


class FGUICommon:
    UI_PREFIX: str = "ui://"
    """
    文本：`ui://`
    """


# endregion FGUI常量定义


# region FGUI其他类

class FGUIUtils:
    @staticmethod
    def get_branch_path_list(project: FGUIProject) -> list[str]:
        """
        获取FGUI项目中的所有分支的路径。
        :param project: FGUI项目实例。
        :return: FGUI项目中的所有分支的路径。
        """

        # 找到目录下，所有以分支前缀开头的文件夹
        branch_path_list = []
        for item in os.listdir(project.project_root_path):
            if item.startswith(FGUIFolderName.ASSETS_BRANCH_PREFIX):
                branch_path = os.path.join(project.project_root_path, item)
                branch_path_list.append(branch_path)

        return branch_path_list

    @staticmethod
    def url_combine(package_id: str, resource_id: str) -> str:
        """
        拼接包ID和资源ID。
        :param package_id: 包ID。
        :param resource_id: 资源ID。
        :return: 合并后的ID。
        """
        return f"{FGUICommon.UI_PREFIX}{package_id}{resource_id}"

    @staticmethod
    def url_split(full_id: str, fgui_branch: FGUIBranch) -> tuple[str, str] | None:
        """
        拆分包ID和资源ID。
        :param full_id: 全ID。
        :param fgui_branch: FGUI分支实例。
        :return: 包ID和资源ID。
        """

        if not full_id.startswith(FGUICommon.UI_PREFIX):
            raise ValueError(f"Invalid full_id: {full_id}")

        full_id = full_id[len(FGUICommon.UI_PREFIX):]

        for package in fgui_branch.package_list:
            if full_id.startswith(package.package_id):
                package_id = package.package_id
                resource_id = full_id[len(package_id):]
                return package_id, resource_id

        return None

    @staticmethod
    def generate_package_id() -> str:
        """
        随机生成一个8位的，由小写字母和数字组成的字符串
        """
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))

    @staticmethod
    def get_package_xml_template(package_id):
        """
        生成一个package.xml文件的模板
        """

        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<packageDescription id="{package_id}">',
            f'  <resources/>',
            '</packageDescription>'
        ]

        return "\n".join(lines)

    @staticmethod
    def format_xml_file(file_path: str):
        """
        根据fgui的xml格式，将文件内容进行格式化
        """

        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read()

            content = content.replace(
                "<?xml version='1.0' encoding='utf-8'?>",
                '<?xml version="1.0" encoding="utf-8"?>')

            content = content.replace(
                "    </displayList>",
                '  </displayList>')

            content = content.replace(
                ' />',
                '/>')

            content = content.replace(
                '&#09;',
                '&#x9;')

            content = content.replace(
                '&#10;',
                '&#xA;')

            content = content.replace(
                '&#13;',
                '&#xD;')

        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)


class FGUIUrl:
    """
    FGUI中的URL，由包ID和资源ID组成。
    """

    # region 特殊方法
    def __init__(self, package_id: str, resource_id: str):
        """
        初始化FGUI URL。
        """
        self._package_id = package_id
        """
        包ID。
        """
        self._resource_id = resource_id
        """
        资源ID。
        """

    def __str__(self):
        return f"ui://{self.package_id}{self.resource_id}"

    # endregion 特殊方法

    # region 属性
    @property
    def package_id(self) -> str:
        """
        包ID。
        """
        return self._package_id

    @property
    def resource_id(self) -> str:
        """
        资源ID。
        """
        return self._resource_id

    @property
    def url(self) -> str:
        """
        URL。
        """
        return f"ui://{self.package_id}{self.resource_id}"
    # endregion 属性


# region FGUI其他类


# region FGUI项目结构类型

class FGUIProject:
    """
    FGUI项目的一个实例，包括了项目的所有信息。
    """

    # region 特殊方法
    def __init__(self, project_file_path: str):
        """
        初始化FGUI项目实例。
        如果加载失败，会抛出异常。
        :param project_file_path: FGUI项目文件（.fairy文件）的路径。
        """
        self._project_file_path: Path = Path(project_file_path)
        """
        FGUI项目文件路径的Path对象实例。
        """

        try:
            self._load_project()
        except Exception as e:
            raise e

    # endregion 特殊方法

    # region 属性
    @property
    def project_file_path(self) -> str:
        """
        FGUI项目文件的路径。
        """
        return str(self._project_file_path)

    @property
    def project_root_path(self) -> str:
        """
        FGUI项目的根目录。
        """
        return str(self._project_file_path.parent)

    @property
    def project_name(self) -> str:
        """
        FGUI项目的名称。
        """
        return self._project_file_path.stem

    # endregion 属性

    # region 私有方法
    def _load_project(self):
        """
        加载FGUI项目。
        """
        # 检查文件是否存在
        if not self._project_file_path.exists():
            raise FileNotFoundError(f"指定的FGUI项目文件：{self._project_file_path}不存在！")

        # 检查是否为FGUI项目文件
        if self._project_file_path.suffix != FGUIExtensions.PROJECT:
            raise ValueError(f"指定的文件不是FGUI项目文件！")

        main_branch_path = os.path.join(self._project_file_path.parent, FGUIFolderName.ASSETS)
        self.main_branch: FGUIBranch = FGUIBranch(main_branch_path)

        # 暂时先不考虑分支的问题
        self.other_branches: list[FGUIBranch] = []
    # endregion 私有方法

    # region 公开方法

    # endregion 公开方法


class FGUIBranch:
    """
    FGUI项目中的一个分支，对应一个分支的文件夹。
    """

    # region 特殊方法
    def __init__(self, branch_root_path: str):
        """
        初始化FGUI分支实例。
        :param branch_root_path: FGUI分支的根目录。
        """
        self._branch_root_path = Path(branch_root_path)
        """
        FGUI分支的根目录的Path对象实例。
        """

        self._is_main_branch: bool = self._branch_root_path.name == FGUIFolderName.ASSETS
        """
        是否为主分支。
        """

        self.package_list: list[FGUIPackage] = []
        """
        包列表。
        """

        self.package_id_dict: dict[str, FGUIPackage] = {}
        """
        以包的ID为键的包字典。
        """
        self.package_name_dict: dict[str, FGUIPackage] = {}
        """
        以包的名称为键的包字典。
        """

        # 加载包
        self._load_packages()

    # endregion 特殊方法

    # region 属性
    @property
    def branch_root_path(self) -> str:
        """
        FGUI分支的根目录。
        """
        return str(self._branch_root_path)

    @property
    def branch_name(self) -> str:
        """
        FGUI分支的名称。
        """
        return self._branch_root_path.name

    @property
    def is_main_branch(self) -> bool:
        """
        是否为主分支。
        """
        return self._is_main_branch

    # 属性

    # region 私有方法
    def _load_packages(self):
        """
        加载分支中的所有包。
        """

        # 获取所有的包文件夹
        all_folder_list: list[Path] = [item for item in self._branch_root_path.iterdir() if item.is_dir()]

        # 仅保留其中有package.xml文件的文件夹
        package_folder_list: list[Path] = []
        for folder in all_folder_list:
            package_xml_path = os.path.join(folder, FGUIFileName.PACKAGE_XML)
            if os.path.exists(package_xml_path):
                package_folder_list.append(folder)

        # 清空数据
        self.package_list.clear()
        self.package_id_dict.clear()
        self.package_name_dict.clear()

        # 加载包
        for folder in package_folder_list:
            package = FGUIPackage(self, str(folder))
            self.package_list.append(package)
            self.package_id_dict[package.package_id] = package
            self.package_name_dict[package.package_name] = package

    # endregion 私有方法

    # region 公开方法
    def reload_packages(self):
        """
        重新加载分支中的所有包。
        """
        self._load_packages()

    def get_package_by_name(self, package_name: str) -> FGUIPackage | None:
        """
        获取指定名称的包。
        :param package_name: 包名称。
        :return: 包实例。
        """
        return self.package_name_dict.get(package_name)

    def get_package_by_id(self, package_id: str) -> FGUIPackage | None:
        """
        获取指定ID的包。
        :param package_id: 包ID。
        :return: 包实例。
        """
        return self.package_id_dict.get(package_id)

    def get_resource_by_path(self, resource_path: str) -> FGUIResource | None:
        """
        获取指定名称的资源。
        :param resource_path: 资源路径。
        :return: 资源实例。
        """

        package: FGUIPackage
        for package in self.package_list:
            if resource_path.startswith(package.package_name):
                target_resource_name: str = resource_path[len(package.package_name):]

                resource: FGUIResource
                for resource in package.package_resources:
                    if target_resource_name == resource.resource_pure_name:
                        return resource

        return None

    def get_resource_by_url(self, resource_url: str) -> FGUIResource | None:
        """
        获取指定URL的资源。
        :param resource_url: 资源ID。
        :return: 资源实例。
        """
        # 如果用了UI的前缀，那就去掉
        if resource_url.startswith(FGUICommon.UI_PREFIX):
            resource_url = resource_url[len(FGUICommon.UI_PREFIX):]

        package: FGUIPackage
        for package in self.package_list:
            if resource_url.startswith(package.package_id):
                target_resource_id: str = resource_url[len(package.package_id):]

                resource: FGUIResource
                for resource in package.package_resources:
                    if target_resource_id == resource.resource_id:
                        return resource

        return None
    # endregion 公开方法


class FGUIPackage:
    """
    FGUI项目中的一个Package，对应一个package.xml文件中的内容。
    """

    # region 特殊方法
    def __init__(self, owner_branch: FGUIBranch, package_root_path: str, is_sub_branch: bool = False):
        """
        初始化FGUI包实例。
        初始化失败会抛出异常。
        :param package_root_path: FGUI包的根目录。
        """

        try:
            self._load_resources(owner_branch, package_root_path, is_sub_branch)
        except Exception as e:
            raise e

    def __str__(self):
        return f"Package: {self.package_name} ({self.package_id})"

    # endregion 特殊方法

    # region 属性
    @property
    def package_root_path(self) -> str:
        """
        FGUI包的根目录。
        """
        return str(self._package_root_path)

    @property
    def package_id(self) -> str:
        """
        FGUI包的ID。
        """
        return self._package_id

    @property
    def package_name(self) -> str:
        """
        FGUI包的名称。
        """
        return self._package_name

    # endregion 属性

    # region 私有方法
    def _load_resources(self, owner_branch: FGUIBranch, package_root_path: str, is_sub_branch: bool):
        """
        加载FGUI包中的资源。
        """

        self.owner_branch: FGUIBranch = owner_branch

        # 检查文件是否存在
        self._package_root_path = Path(package_root_path)
        """
        FGUI包根目录的Path对象实例。
        """
        if not self._package_root_path.exists():
            raise FileNotFoundError(f"指定的FGUI包{package_root_path}不存在！")

        # 检查是否为FGUI包文件
        file_name = FGUIFileName.PACKAGE_BRANCH_XML if is_sub_branch else FGUIFileName.PACKAGE_XML

        self._package_xml_path = Path(os.path.join(package_root_path, file_name))
        """
        FGUI包的`package.xml`文件的Path对象实例。
        """
        if not self._package_xml_path.exists():
            raise FileNotFoundError(f"指定的文件不是FGUI包文件，找不到{file_name}文件！")

        self._package_name: str = self._package_root_path.name
        """
        FGUI包的名称。
        """

        # 读取xml文件
        self._xml_content: ElementTree = ET.parse(self._package_xml_path)
        xml_root: Element = self._xml_content.getroot()

        self._package_id: str = xml_root.attrib["id"]
        """
        FGUI包的ID。
        """

        self.package_resources: list[FGUIResource] = []
        """
        FGUI包的资源列表。
        """

        # 遍历xml文件根节点下的resources节点中的所有节点
        resource_elements: Element = xml_root.find("resources")

        for resource_element in resource_elements:
            self.package_resources.append(FGUIResource(self, resource_element))

    # endregion 私有方法

    # region 公开方法
    def get_resource_by_name(self, resource_name: str) -> FGUIResource | None:
        """
        获取指定名称的资源。
        :param resource_name: 资源名称。
        :return: 资源实例。
        """
        resource: FGUIResource
        for resource in self.package_resources:
            if resource_name == resource.resource_name:
                return resource

        return None

    def get_resource_by_id(self, resource_id: str) -> FGUIResource | None:
        """
        获取指定ID的资源。
        :param resource_id: 资源ID。
        :return: 资源实例。
        """
        resource: FGUIResource
        for resource in self.package_resources:
            if resource_id == resource.resource_id:
                return resource

    def get_references(self, ignore_self_package: bool = True) -> tuple[list[FGUIUrl], list[str]]:
        """
        获取当前包内，所有资源对于其他包的资源引用的列表。
        """
        reference_url: list[FGUIUrl] = []
        invalid_url: list[str] = []

        resource: FGUIResource
        for resource in self.package_resources:
            resource_url_list, resource_invalid_url_list = resource.get_references(ignore_self_package)

            reference_url.extend(resource_url_list)
            invalid_url.extend(resource_invalid_url_list)

        return reference_url, invalid_url
    # endregion 公开方法


class FGUIResource:
    """
    FGUI项目中，存储的每个组件、图片等，都是一个Resource对象。
    """

    # region 特殊方法
    def __init__(self, owner_package: FGUIPackage, xml_node: Element):
        """
        初始化FGUI资源实例。
        :param owner_package: 所属的FGUI包。
        :param xml_node: FGUI资源的xml节点。
        """

        self.owner_package: FGUIPackage = owner_package
        """
        所属的FGUI包。
        """

        self._xml_node: Element = xml_node
        """
        FGUI资源的xml节点。
        """

        self.object_list: list[FGUIObject] = []
        """
        FGUI资源中的对象列表。
        """

        self.error_file: bool = False

        # 如果是组件，加载对象
        if self._xml_node.tag == "component":
            self._load_objects()

        self.resource_path: Path = Path(self.full_path)
        """
        FGUI资源的文件路径。
        """

    def __str__(self):
        return f"Resource: {self._xml_node.attrib['name']} ({self._xml_node.attrib['id']})"

    # endregion 特殊方法

    # region 属性
    @property
    def relative_path(self) -> str:
        """
        获取资源相对于包目录的路径。
        形式类似于`aaa/bbb/ccc.png`。
        """

        """
        在package.xml文件里，记录的信息类似于：
        name="AAA.png" path="/aaa/bbb/"
        如果文件就在根目录下，则记录为：
        name="BBB.xml" path="/"
        由于转义的问题，还需要处理一下斜杠
        """
        file_name = self._xml_node.attrib["name"]
        relative_path = self._xml_node.attrib["path"]

        # 不要开头的斜杠
        if relative_path.startswith("/"):
            relative_path = relative_path[1:]

        # 将所有的`/`替换为系统的分隔符
        relative_path = relative_path.replace("/", os.sep)

        return relative_path + file_name

    @property
    def full_path(self) -> str:
        """
        资源的完整路径。
        """
        return os.path.join(self.owner_package.package_root_path, self.relative_path)

    @property
    def reference_path(self) -> str:
        """
        获取资源的引用路径。由包名和无后缀的文件名组成。形式类似于：`ui://[PackageName]/[ResourceName]`。
        """
        return f"{FGUICommon.UI_PREFIX}{self.owner_package.package_name}/{self.resource_path.stem}"

    @property
    def reference_url(self) -> str:
        """
        获取资源的引用URL。形式类似于：`ui://[PackageID][ResourceID]`。
        """
        return f"{FGUICommon.UI_PREFIX}{self.owner_package.package_id}{self.resource_id}"

    @property
    def reference_path_no_prefix(self) -> str:
        """
        获取资源的引用路径。由包名和无后缀的文件名组成。形式类似于：`[PackageName]/[ResourceName]`。
        """
        return f"{self.owner_package.package_name}/{self.resource_path.stem}"

    @property
    def reference_url_no_prefix(self) -> str:
        """
        获取资源的引用URL。形式类似于：`[PackageID][ResourceID]`。
        """

        return f"{self.owner_package.package_id}{self.resource_id}"

    @property
    def file_exists(self) -> bool:
        """
        FGUI资源文件是否存在。
        """
        return os.path.exists(self.full_path)

    @property
    def resource_id(self) -> str:
        """
        FGUI资源的ID。
        """
        return self._xml_node.attrib["id"]

    @property
    def resource_name(self) -> str:
        """
        FGUI资源的名称。
        """
        return self._xml_node.attrib["name"]

    @property
    def resource_pure_name(self) -> str:
        """
        获取资源的纯名称，不包含后缀。
        """
        return self.resource_path.stem

    # endregion 属性

    # region 私有方法
    def _load_objects(self):
        """
        加载FGUI资源中的对象。
        """
        self.object_list.clear()

        # 如果文件存在，才加载
        if not self.file_exists:
            return

        # 读取xml文件
        try:
            self._xml_content: ElementTree = ET.parse(self.full_path)
            xml_root: Element = self._xml_content.getroot()

            display_list: Element = xml_root.find("displayList")

            # 极特殊的情况，没有displayList节点，那就直接跳过
            if display_list is None:
                return

            for display_object in display_list:
                fgui_object = FGUIObject(self, display_object)
                self.object_list.append(fgui_object)
        except Exception as e:
            print(f"xml file format error: {self.full_path}")
            self.error_file = True

    # endregion 私有方法

    # region 公开方法
    def get_references(self, ignore_self_package: bool = True, ignore_repeat: bool = True) -> tuple[
        list[FGUIUrl], list[str]]:
        """
        获取当前资源中，所有对其他资源的引用。
        :param ignore_self_package: 是否忽略自己包的资源。
        :param ignore_repeat: 是否忽略重复的引用。
        :return: 引用列表。
        """
        reference_url: list[FGUIUrl] = []
        invalid_url: list[str] = []

        # 遍历每个对象，获取引用
        for fgui_object in self.object_list:
            obj_url_list, obj_invalid_url_list = fgui_object.get_references(ignore_self_package, ignore_repeat)

            reference_url.extend(obj_url_list)
            invalid_url.extend(obj_invalid_url_list)

        return reference_url, invalid_url
    # endregion 公开方法


class FGUIObject:
    """
    在一个Component类型的FGUIResource中，内部的每一个对象都是一个FGUIObject。
    """

    # region 特殊方法
    def __init__(self, parent_resource: FGUIResource, xml_node: Element):
        """
        初始化FGUI对象实例。
        """

        self.parent_resource: FGUIResource = parent_resource

        self._xml_node: Element = xml_node

    def __str__(self):
        return f"{self.object_name} ({self.object_id})"

    # endregion 特殊方法

    # region 属性
    @property
    def object_id(self) -> str:
        """
        对象的ID。
        """
        return self._xml_node.attrib["id"]

    @property
    def object_name(self) -> str:
        """
        对象的名称。
        """
        return self._xml_node.attrib["name"]

    # endregion 属性

    # region 私有方法

    # endregion 私有方法

    # region 公开方法
    def get_references(self, ignore_self_package: bool = True, ignore_repeat: bool = True) -> tuple[
        list[FGUIUrl], list[str]]:
        """
        获取当前对象，对其他资源的引用。
        返回值为，有效url的列表，和无效url的列表。
        """
        # 能查到引用的资源
        reference_url: list[FGUIUrl] = []
        # 查不到引用的资源
        invalid_url: list[str] = []

        # 如果自身有src属性，则代表有引用
        self_url: FGUIUrl | None = None
        if "src" in self._xml_node.attrib:
            self_src: str = self._xml_node.attrib["src"]
            # 再检查自己是否有pkg属性
            # 如果有就是引用了其他包的资源
            if "pkg" in self._xml_node.attrib:
                self_pkg = self._xml_node.attrib["pkg"]
                self_url = FGUIUrl(self_pkg, self_src)
            # 如果没有，就是引用了自己包的资源，
            else:
                if not ignore_self_package:
                    self_url = FGUIUrl(self.parent_resource.owner_package.package_id, self_src)

        # 检查自己的资源是否存在，如果不存在也添加到无效列表里
        if self_url is not None:
            self_url_pkg = self.parent_resource.owner_package.owner_branch.get_package_by_id(self_url.package_id)
            if self_url_pkg is None:
                invalid_url.append(self_url.url)
            else:
                self_url_src = self_url_pkg.get_resource_by_id(self_url.resource_id)
                if self_url_src is None:
                    invalid_url.append(self_url.url)
                else:
                    reference_url.append(self_url)

        # 遍历每个属性，以及所有子节点的所有属性
        attribute_need_check = []
        attribute_need_check.extend(self._xml_node.attrib.values())
        for child_node in self._xml_node:
            attribute_need_check.extend(child_node.attrib.values())

        for attribute in attribute_need_check:
            # 有可能是控制器里的引用，可能是多个url组合，用`|`分割，确定一下是否需要拆分
            for string_part in attribute.split("|"):
                if string_part.startswith(FGUICommon.UI_PREFIX):
                    split_result: tuple[str, str] | None = FGUIUtils.url_split(string_part,
                                                                               self.parent_resource.owner_package.owner_branch)

                    if split_result is not None:
                        pkg_id, res_id = split_result
                        reference_url.append(FGUIUrl(pkg_id, res_id))
                    else:
                        invalid_url.append(string_part)

        # 将引用去重
        if ignore_repeat:
            reference_url_dict: dict[str, FGUIUrl] = dict()
            for url in reference_url:
                reference_url_dict[url.url] = url

            reference_url = list(reference_url_dict.values())

            invalid_url = list(set(invalid_url))

        return reference_url, invalid_url
    # endregion 公开方法

# endregion FGUI项目结构类型
