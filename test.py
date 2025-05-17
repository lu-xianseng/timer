import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class RichTextDisplay(QMainWindow):
    def __init__(self, html_content=None):
        super().__init__()
        self.initUI(html_content)

    def initUI(self, html_content):
        # 设置窗口标题和大小
        self.setWindowTitle('富文本显示')
        self.setGeometry(300, 300, 600, 400)

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建文本浏览器（不可编辑的富文本组件）
        self.text_browser = QTextBrowser()
        # 如果提供了HTML内容，则显示它
        if html_content:
            self.text_browser.setHtml(html_content)
        else:
            # 否则显示一个示例
            self.text_browser.setHtml("""
                <h1 style="color: #336699;">富文本示例</h1>
                <p>这是一个<strong>粗体文本</strong>，这是一个<em>斜体文本</em>。</p>
                <p>你可以显示<strong style="color: red;">彩色文本</strong>、<a href="https://example.com">链接</a>等。</p>
                <ul>
                    <li>项目1</li>
                    <li>项目2</li>
                    <li>项目3</li>
                </ul>
            """)

        # 设置中文字体支持
        font = QFont("SimHei", 10)
        self.text_browser.setFont(font)

        layout.addWidget(self.text_browser)


def show_rich_text(html_content=None):
    """便捷函数：显示给定的HTML内容"""
    app = QApplication(sys.argv)
    window = RichTextDisplay(html_content)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # 示例：显示自定义HTML内容
    custom_html = """
        <h2 style="color: #4CAF50;">自定义富文本内容</h2>
        <p>你可以直接调用show_rich_text函数并传入HTML字符串。</p>
        <p>支持所有HTML标签，包括<img src="https://picsum.photos/200/100" alt="示例图片">。</p>
    """
    show_rich_text(custom_html)
    # 或者直接运行：show_rich_text() 来使用默认示例