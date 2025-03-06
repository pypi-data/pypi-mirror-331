from xl_word.word_file import WordFile
from jinja2 import Template
from pathlib import Path
import math 


class Sheet(WordFile):
    """Word表单对象，用于处理Word模板文件的渲染和XML操作"""

    TEMPLATE_FUNCTIONS = {
        'enumerate': enumerate,
        'len': len, 
        'isinstance': isinstance,
        'tuple': tuple,
        'list': list,
        'str': str,
        'float': float,
        'int': int,
        'range': range,
        'ceil': math.ceil,
        'type': type
    }

    def __init__(self, tpl_path, xml_folder=None):
        """初始化Sheet对象
        
        Args:
            tpl_path: Word模板文件路径
            xml_folder: 可选的XML模板文件夹路径
        """
        super().__init__(tpl_path)
        self.xml_folder = xml_folder

    def render_template(self, template_content, data):
        """渲染Jinja2模板
        
        Args:
            template_content: 模板内容字符串
            data: 用于渲染的数据字典
            
        Returns:
            str: 渲染后的内容
        """
        rendered = Template(template_content).render(
            **data, 
            **self.TEMPLATE_FUNCTIONS
        )
        return rendered.replace(' & ', ' &amp; ')

    def get_xml_template(self, xml_filename):
        """获取XML模板内容
        
        Args:
            xml_filename: XML文件名(不含扩展名)
            
        Returns:
            str: XML模板内容
        """
        if self.xml_folder:
            xml_path = Path(self.xml_folder) / f'{xml_filename}.xml'
            return self._read_external_template(xml_path)
        return self._read_internal_template(xml_filename)

    def _read_external_template(self, xml_path):
        """读取外部XML模板文件
        
        Args:
            xml_path: XML文件完整路径
            
        Returns:
            str: XML文件内容
        """
        with open(xml_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _read_internal_template(self, xml_filename):
        """读取Word文档内部的XML模板
        
        Args:
            xml_filename: XML文件名
            
        Returns:
            str: XML文件内容
        """
        return self[f'word/{xml_filename}.xml'].decode()

    def render_xml(self, xml_filename, data):
        try:
            xml_template = self.get_xml_template(xml_filename)
            xml_string = self.render_template(xml_template, data).encode()
            self[f'word/{xml_filename}.xml'] = xml_string
            return xml_string
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def render_and_add_xml(self, xml_type, data, relation_id=None):
        """渲染并添加新的XML文件到文档
        
        Args:
            xml_type: XML类型
            data: 渲染数据
            relation_id: 可选的关系ID
            
        Returns:
            str: 生成的关系ID
        """
        xml_content = self.render_template(
            self.get_xml_template(xml_type),
            data
        )
        return self.add_xml(xml_type, xml_content, relation_id)

    def render(self, data):
        for xml_type in ('header', 'footer', 'document'):
            self.render_xml(xml_type, data)
        return self