# 个人自用小工具 🛠️✨
![License](https://img.shields.io/badge/license-MIT-green.svg) <!-- 请替换为您的实际许可证 -->
一些方便自己使用的 Python 小脚本集合。
---
## 🎯 核心功能
### ✨ 换行转逗号分割
-   **功能**: 从系统剪贴板读取文本内容。
-   **处理**: 将文本中的每一行（以换行符 `\n` 分隔）转换为以逗号 `,` 分隔的单行字符串。
    -   例如:
        ```
        abcd
        efg
        hi
        ```
        将被转换为:
        ```
        abcd,efg,hi,
        ```
-   **输出**: 自动将处理后的字符串复制回系统剪贴板。
### ✨ 音频截取与拼接
-   **功能**: 提供一个命令行界面来处理音频文件。
-   **主要操作**:
    1.  **截取**: 根据用户设定的开始和结束时间，截取指定音频文件。
    2.  **拼接**: 将多个音频文件按顺序拼接成一个单独的文件。
-   **交互菜单**:
    ```
    1. 设置输入目录
    2. 设置输出目录
    3. 扫描并显示音频文件
    4. 截取音频
    5. 拼接音频
    6. 查看已处理文件
    7. 帮助
    0. 退出程序
    ```
### ✨ 更多工具...
-   正在构思和开发中，敬请期待！🚀
---
## 🚀 技术栈
-   **主要语言**: Python 3

---
## 🛠️ 安装与使用
1.  **克隆仓库** (如果您将其托管在 GitHub 等平台):
    ```bash
    git clone https://github.com/faithererer/myTools.git
    cd myTools-master
    ```
2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **运行脚本**: (假设主脚本名为 `main.py` 或根据您的实际情况修改)
    进入对应目录 运行:
    ```bash
    python main.py 
    ```
    或者双击运行`start.bat`
---
## 🤝 贡献
欢迎提出 Issue 或 Pull Request！
---
## 📄 许可证
本项目采用 [MIT](LICENSE) 许可证。 <!-- 请确保您有 LICENSE 文件或更新此链接/名称 -->
