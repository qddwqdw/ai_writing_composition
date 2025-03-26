from openai import OpenAI
import time
from pathlib import Path
import json

class EssayBookGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url='https://api.siliconflow.cn/v1/'
        )
        self.model = 'deepseek-ai/DeepSeek-V3'
        self.template = {
            "narrative": """你是一位中考作文专家，请根据以下要求创作记叙文：
主题：{theme}
要求：
1. 使用【{object}】作为核心意象
2. 包含3个感官细节（视觉/听觉/触觉各1个）
3. 采用双线结构（明线：{object}变化，暗线：情感变化）
4. 结尾用"原来..."句式升华""",
            
            "argumentative": """你是一位中考作文专家，请根据以下要求创作议论文：
主题：{theme}
要求：
1. 使用"现象-论点-正反论证-结论"结构
2. 包含1句古诗文引用和1个现代案例
3. 结尾使用排比句式
4. 关键词：{keywords}"""
        }

        self.theme_matrix = [
            {"分类": "成长类", "主题": ["坚持", "挫折", "自我突破"], "关键词": ["成长", "勇气"]},
            {"分类": "情感类", "主题": ["亲情", "师生情", "陌生人温暖"], "关键词": ["温暖", "感动"]},
            {"分类": "社会类", "主题": ["传统文化", "科技伦理", "环境保护"], "关键词": ["传承", "责任"]}
        ]

    def call_deepseek(self, prompt, retry=3):
        for attempt in range(retry):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2000,
                    stream=False
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"尝试 {attempt+1} 失败，错误：{str(e)}")
                time.sleep(2)
        return None

    def generate_single_essay(self, theme_info, genre):
        """生成单篇作文并返回格式化结果"""
        prompt = self.template[genre].format(
            theme=theme_info["主题"],
            object=theme_info["关键词"][0],
            keywords="、".join(theme_info["关键词"])
        )
        content = self.call_deepseek(prompt)
        if not content:
            return None

        essay_data = {
            "content": content.strip(),
            "metadata": {
                "生成时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                "文体": "记叙文" if genre == "narrative" else "议论文",
                "关键词": theme_info["关键词"]
            }
        }

        # 实时输出到控制台
        print(f"\n=== 生成的{essay_data['metadata']['文体']} ===")
        print(f"分类：{theme_info['分类']}")
        print(f"主题：{theme_info['主题']}")
        print(f"生成时间：{essay_data['metadata']['生成时间']}")
        print("内容预览：")
        print(content[:200] + "..." if len(content) > 200 else content)
        print("="*50 + "\n")
        
        return essay_data

    def update_markdown(self, full_data):
        """更新并保存Markdown文件"""
        md_content = self.build_markdown(full_data)
        Path("中考范文库.md").write_text(md_content, encoding="utf-8")
        print("范文库已更新保存")

    def build_markdown(self, data):
        """构建完整的Markdown内容"""
        md = "# 中考双文体范文库\n\n"
        for category in data:
            md += f"## {category['分类']}\n\n"
            for theme in category["themes"]:
                md += f"### 主题：{theme['主题']}\n"
                md += f"**关键词**：`{'、'.join(theme['关键词'])}`\n\n"
                
                if 'narrative' in theme:
                    md += "#### 记叙文\n---\n" + theme['narrative']['content'] + "\n\n---\n\n"
                if 'argumentative' in theme:
                    md += "#### 议论文\n---\n" + theme['argumentative']['content'] + "\n\n---\n\n"
        return md

    def generate_book(self):
        """主生成函数，实现实时保存"""
        full_data = []
        
        for category_info in self.theme_matrix:
            current_category = {
                "分类": category_info["分类"],
                "themes": []
            }
            
            for theme in category_info["主题"]:
                theme_data = {
                    "分类": category_info["分类"],
                    "主题": theme,
                    "关键词": category_info["关键词"]
                }
                
                # 生成记叙文
                narrative = self.generate_single_essay(theme_data, "narrative")
                if narrative:
                    theme_data["narrative"] = narrative
                    self._update_data(full_data, current_category, theme_data)
                    self.update_markdown(full_data)
                    time.sleep(1)
                
                # 生成议论文
                argumentative = self.generate_single_essay(theme_data, "argumentative")
                if argumentative:
                    theme_data["argumentative"] = argumentative
                    self._update_data(full_data, current_category, theme_data)
                    self.update_markdown(full_data)
                    time.sleep(1)
                
                # 添加到当前分类
                current_category["themes"].append(theme_data)
            
            # 更新总数据
            existing = next((c for c in full_data if c["分类"] == current_category["分类"]), None)
            if not existing:
                full_data.append(current_category)

        # 最终保存确保完整性
        self.update_markdown(full_data)

    def _update_data(self, full_data, current_category, theme_data):
        """更新数据存储结构"""
        # 查找是否已存在该分类
        target_category = next((c for c in full_data if c["分类"] == current_category["分类"]), None)
        
        if not target_category:
            full_data.append(current_category)
            return
        
        # 查找是否已存在该主题
        existing_theme = next((t for t in target_category["themes"] if t["主题"] == theme_data["主题"]), None)
        if existing_theme:
            existing_theme.update(theme_data)
        else:
            target_category["themes"].append(theme_data)

if __name__ == "__main__":
<<<<<<< HEAD
    DEEPSEEK_API_KEY = '填入你的API_KEY'
=======
    DEEPSEEK_API_KEY = 'sk-tqolkxkjakcnncbswogtilkjuzsztsobuizyuqmzfjgictkd'
>>>>>>> acec26172801e0e2c4d6633ae611c223b1d23fc0
    
    generator = EssayBookGenerator(DEEPSEEK_API_KEY)
    generator.generate_book()