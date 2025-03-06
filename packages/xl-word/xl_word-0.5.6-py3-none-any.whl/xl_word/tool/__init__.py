from xl_word.tool.gui import *
from xl_word.tool.utility import SuperWordFile
import os


class WordTemplateEditor:
    """Word模板编辑器"""

    def __init__(self):
        """初始化编辑器"""
        self.app = App({
            'title': 'XiLong DOCX Toolkit',
            'size': (420, 330),
            'loc': (500, 300)
        })
        self.root = self.app.instance
        self._init_ui()

    def _init_ui(self):
        """初始化UI界面"""
        self.main_frame = Frame(self.root, relief='ridge', borderwidth=1)
        self.main_frame.pack(fill=BOTH, expand=True)
        self._create_input_fields()
        self._create_buttons()

    def _create_input_fields(self):
        """创建输入字段"""
        # 创建拖拽区域
        self.drop_label = Label(self.main_frame, text="拖拽DOCX文件到这里", relief="solid")
        self.drop_label.pack()
        self.drop_label.place(x=30, y=30, width=350, height=40)
        
        # 绑定拖拽事件
        self.drop_label.drop_target_register("DND_Files")
        self.drop_label.dnd_bind('<<Drop>>', self._on_drop)

    def _create_buttons(self):
        """创建所有按钮"""
        # 提取按钮组
        extract_buttons = [
            ('提取document', self._extract_document, 30),
            ('提取header', self._extract_header, 155),
            ('提取footer', self._extract_footer, 280)
        ]
        
        for text, command, x in extract_buttons:
            btn = self.app.button(
                self.main_frame, text, command, width=13
            )
            btn.pack()
            btn.place(x=x, y=90)

        # 转换按钮组
        convert_buttons = [
            ('DOCX转XML(竖向)', self._word2xml_v, 30, 150),
            ('DOCX转XML(横向)', self._word2xml_h, 220, 150),
            ('XML转DOCX(竖向)', self._xml2word_v, 30, 190),
            ('XML转DOCX(横向)', self._xml2word_h, 220, 190)
        ]

        for text, command, x, y in convert_buttons:
            btn = self.app.button(
                self.main_frame, text, command, width=20
            )
            btn.pack()
            btn.place(x=x, y=y)

    def _on_drop(self, event):
        """处理文件拖拽"""
        file_path = event.data
        if file_path.endswith('.docx'):
            self.current_file = file_path
            self.drop_label.config(text=f"当前文件: {os.path.basename(file_path)}")
        else:
            self.app.alert("错误", "请拖拽DOCX文件(.docx)")

    # DOCX文件操作方法
    def _get_edit_input(self):
        """获取编辑输入"""
        if not hasattr(self, 'current_file'):
            self.app.alert("错误", "请先拖拽DOCX文件")
            return None, None
            
        folder = os.path.dirname(self.current_file)
        file = os.path.basename(self.current_file)
        return folder, file

    def _extract_document(self):
        """提取document.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            SuperWordFile(folder, file).extract('document.xml')

    def _extract_header(self):
        """提取header.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            SuperWordFile(folder, file).extract('header.xml')

    def _extract_footer(self):
        """提取footer.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            SuperWordFile(folder, file).extract('footer.xml')

    def _word2xml_h(self):
        """DOCX转XML(横向)"""
        SuperWordFile.word2xml('h')

    def _word2xml_v(self):
        """DOCX转XML(竖向)"""
        SuperWordFile.word2xml('v')

    def _xml2word_h(self):
        """XML转DOCX(横向)"""
        SuperWordFile.xml2word('h')

    def _xml2word_v(self):
        """XML转DOCX(竖向)"""
        SuperWordFile.xml2word('v')

    def run(self):
        """运行编辑器"""
        self.app.run()


if __name__ == '__main__':
    editor = WordTemplateEditor()
    editor.run()