
# CLI Notebook - 命令行笔记管理工具

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个基于Python的命令行笔记应用，使用`questionary`库构建交互界面，支持笔记的增删查改和持久化存储。

## ✨ 功能特性

- **核心功能**
  - 📝 添加富文本笔记（标题+内容）
  - 🔍 全文搜索（支持标题和内容关键词）
  - 📖 时间线浏览（按时间倒序排列）
  - 🗑️ 安全删除（带确认提示）
  
- **增强特性**
  - 🎨 自定义命令行界面样式
  - ⏱️ 自动时间戳记录
  - 💾 JSON数据持久化存储
  - 📦 跨平台支持（Windows/Linux/macOS/Android Termux）

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. 使用pip安装
```
pip install heartflow
```

2. 下载[Releases](https://github.com/Crillerium/heartflow/releases)安装
```
pip install path/to/file.whl
```

### 使用指南
```bash
# 启动应用
$ hf
或
$ python -m heartflow

# 主菜单示例
[📔 欢迎使用命令行记事本]

请选择操作:
  添加笔记
  查看所有笔记
  搜索笔记
  删除笔记
  退出
```

## ⚙️ 配置选项

自定义界面样式（修改`custom_style`变量）：
```python
custom_style = Style([
    ('qmark', 'fg:#FF9D00 bold'),   # 问题标记颜色
    ('pointer', 'fg:#00FF00 bold'), # 选择指针颜色
    ('answer', 'fg:#0000FF bold')   # 答案文本颜色
])
```

## 📌 注意事项

1. 数据文件默认存储在程序目录的`notes.json`
2. 强烈建议定期备份数据文件
3. 在Termux中使用时请确保存储权限：
   ```bash
   termux-setup-storage
   ```

## 📜 许可证

本项目采用 [MIT License](LICENSE)

---

> 提示：按方向键导航菜单，Enter键确认选择