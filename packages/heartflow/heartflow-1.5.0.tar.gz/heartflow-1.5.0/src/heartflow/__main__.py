import json
import os
from datetime import datetime
from questionary import prompt, select, text, confirm
from questionary import Style
import importlib.resources as pkg

# 自定义样式
custom_style = Style([
    ('qmark', 'fg:#FF9D00 bold'),      # 问题标记颜色
    ('question', 'bold'),              # 问题文本
    ('answer', 'fg:#008000 bold'),     # 回答文本
    ('pointer', 'fg:#FF9D00 bold'),    # 选择指针
])

with pkg.path("heartflow","notes.json") as f:
    NOTES_FILE = f

def load_notes():
    """加载所有笔记"""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []

def save_notes(notes):
    """保存笔记到文件"""
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)

def add_note():
    """添加新笔记"""
    questions = [
        {
            'type': 'text',  # 明确指定问题类型
            'name': 'title',  # 答案字典的键名
            'message': '请输入笔记标题',
            'validate': lambda t: True if t else "标题不能为空"
        },
        {
            'type': 'text',
            'name': 'content',
            'message': '请输入笔记内容'
        }
    ]
    answers = prompt(questions, style=custom_style)
    
    note = {
        "title": answers["title"],
        "content": answers["content"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    print("\n✅ 笔记已保存！\n")

def view_notes():
    """查看所有笔记"""
    notes = load_notes()
    if not notes:
        print("\n📭 当前没有笔记\n")
        return
    
    # 按时间倒序排列
    notes_sorted = sorted(notes, key=lambda x: x["timestamp"], reverse=True)
    
    for idx, note in enumerate(notes_sorted, 1):
        print(f"\n📖 笔记 {idx}")
        print(f"标题: {note['title']}")
        print(f"时间: {note['timestamp']}")
        print(f"内容:\n{note['content']}\n")
        print("-" * 40)

def search_notes():
    """搜索笔记"""
    keyword = text("搜索关键词:", style=custom_style).ask()
    if not keyword:
        print("\n⚠️ 请输入搜索关键词\n")
        return
    
    notes = load_notes()
    results = [
        note for note in notes
        if keyword.lower() in note["title"].lower() 
        or keyword.lower() in note["content"].lower()
    ]
    
    if not results:
        print(f"\n🔍 没有找到包含 '{keyword}' 的笔记\n")
        return
    
    print(f"\n找到 {len(results)} 条相关笔记:")
    for idx, note in enumerate(results, 1):
        print(f"\n🔍 结果 {idx}")
        print(f"标题: {note['title']}")
        print(f"时间: {note['timestamp']}")
        print(f"内容:\n{note['content'][:50]}...\n")
        print("-" * 40)

def delete_note():
    """删除笔记"""
    notes = load_notes()
    if not notes:
        print("\n📭 当前没有可删除的笔记\n")
        return
    
    choices = [f"{note['title']} ({note['timestamp']})" for note in notes]
    selected = select(
        "选择要删除的笔记:",
        choices=choices,
        style=custom_style
    ).ask()
    
    if confirm("⚠️ 确定要删除这个笔记吗？", style=custom_style).ask():
        index = choices.index(selected)
        del notes[index]
        save_notes(notes)
        print("\n🗑️ 笔记已删除！\n")

def main():
    """主程序"""
    print("\n📔 欢迎使用命令行记事本\n")
    
    while True:
        action = select(
            "请选择操作:",
            choices=[
                {"name": "添加笔记", "value": "add"},
                {"name": "查看所有笔记", "value": "view"},
                {"name": "搜索笔记", "value": "search"},
                {"name": "删除笔记", "value": "delete"},
                {"name": "退出", "value": "exit"}
            ],
            style=custom_style
        ).ask()

        if action == "add":
            add_note()
        elif action == "view":
            view_notes()
        elif action == "search":
            search_notes()
        elif action == "delete":
            delete_note()
        elif action == "exit":
            print("\n👋 感谢使用，再见！\n")
            break

if __name__ == "__main__":
    main()