#!/usr/bin/env python3
"""
能力库自动生成工具 - AI 生成能力库

功能：
- 基于分析结果自动生成能力库
- 结构化输出（JSON 格式）
- Markdown 格式输出
- 质量验证

依赖：
- requests (用于调用 AI API)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests

# ── 配置 ───────────────────────────────────────────────────

# 能力库模板
ABILITY_LIBRARY_TEMPLATE = {
    "name": "",
    "role": "",
    "version": "1.0",
    "created_at": "",
    "updated_at": "",
    "style": {
        "tone": "",
        "pace": "",
        "approach": "",
        "characteristics": [],
    },
    "skills": [],
    "language_patterns": {
        "常用开场": [],
        "常用追问": [],
        "常用回应": [],
        "常用总结": [],
        "口头禅": [],
        "经典句式": [],
    },
    "values": {
        "事业观": "",
        "情感观": "",
        "成长观": "",
        "世界观": "",
    },
    "thinking_framework": {
        "问题分析": "",
        "决策方式": "",
        "沟通策略": "",
    },
    "knowledge_domains": [],
    "examples": [],
}

# ── AI 生成器 ───────────────────────────────────────────────────


class AIGenerator:
    """AI 内容生成器"""
    
    def __init__(self, api_provider: str = "qwen"):
        """
        初始化 AI 生成器
        
        Args:
            api_provider: API 提供商 (qwen, openai, etc.)
        """
        self.api_provider = api_provider
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")  # 通义千问
    
    def generate_with_ai(
        self,
        prompt: str,
        system_prompt: str = "你是一个专业的内容分析助手。",
        max_tokens: int = 2000,
    ) -> str:
        """
        使用 AI 生成内容
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            max_tokens: 最大 token 数
        
        Returns:
            生成的内容
        """
        if self.api_provider == "qwen":
            return self._generate_qwen(prompt, system_prompt, max_tokens)
        else:
            raise ValueError(f"不支持的 API 提供商：{self.api_provider}")
    
    def _generate_qwen(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
    ) -> str:
        """调用通义千问 API"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        
        result = resp.json()
        return result["output"]["text"]


# ── 能力库生成器 ───────────────────────────────────────────────────


class AbilityLibraryGenerator:
    """能力库生成器"""
    
    def __init__(self, ai_generator: Optional[AIGenerator] = None):
        """
        初始化能力库生成器
        
        Args:
            ai_generator: AI 生成器实例
        """
        self.ai_generator = ai_generator or AIGenerator()
    
    def generate_from_analysis(
        self,
        person_name: str,
        analysis_results: Dict[str, Any],
        research_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        基于分析结果生成能力库
        
        Args:
            person_name: 人物姓名
            analysis_results: NLP 分析结果
            research_data: 研究数据（百科、新闻等）
        
        Returns:
            能力库字典
        """
        print(f"\n🤖 正在为 {person_name} 生成能力库...")
        
        # 初始化能力库
        library = json.loads(json.dumps(ABILITY_LIBRARY_TEMPLATE))
        library["name"] = person_name
        library["created_at"] = datetime.now().isoformat()
        library["updated_at"] = datetime.now().isoformat()
        
        # 1. 从 NLP 分析结果提取语言模式
        print("  - 提取语言模式...")
        if "language_patterns" in analysis_results:
            lp = analysis_results["language_patterns"]
            
            # 口头禅
            if "catchphrases" in lp:
                library["language_patterns"]["口头禅"] = [
                    p["phrase"] for p in lp["catchphrases"].get("catchphrases", [])[:10]
                ]
            
            # 句式特征
            if "sentence_patterns" in lp:
                sp = lp["sentence_patterns"]
                if "examples" in sp:
                    library["language_patterns"]["常用追问"] = sp["examples"].get("questions", [])[:5]
                    library["language_patterns"]["经典句式"] = sp["examples"].get("parallel_sentences", [])[:5]
            
            # 情感倾向
            if "sentiment" in lp:
                sentiment = lp["sentiment"]
                if sentiment["sentiment"] == "positive":
                    library["style"]["tone"] = "积极、鼓励性"
                elif sentiment["sentiment"] == "negative":
                    library["style"]["tone"] = "严肃、批判性"
                else:
                    library["style"]["tone"] = "中性、客观"
        
        # 2. 使用 AI 生成能力库内容
        print("  - AI 生成能力描述...")
        library = self._ai_generate_skills(library, research_data)
        
        print("  - AI 生成价值观和思维框架...")
        library = self._ai_generate_values(library, research_data)
        
        print("  - AI 生成知识领域...")
        library = self._ai_generate_knowledge(library, research_data)
        
        # 3. 生成示例
        print("  - 生成对话示例...")
        library["examples"] = self._generate_examples(person_name, library)
        
        return library
    
    def _ai_generate_skills(
        self,
        library: Dict[str, Any],
        research_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """AI 生成技能列表"""
        prompt = f"""
基于以下研究资料，分析这个人物的核心技能和专业能力。

要求：
1. 列出 3-6 个核心技能
2. 每个技能包含：名称、描述、2-3 个具体例子
3. 以 JSON 格式输出，格式如下：
[
  {{
    "name": "技能名称",
    "description": "技能描述",
    "examples": ["例子 1", "例子 2"]
  }}
]

研究资料摘要：
{json.dumps(research_data, ensure_ascii=False, indent=2)[:2000]}

请直接输出 JSON 数组，不要其他内容。
"""
        
        try:
            response = self.ai_generator.generate_with_ai(prompt)
            # 提取 JSON
            json_match = response.strip()
            if json_match.startswith("```json"):
                json_match = json_match[7:-3]
            
            skills = json.loads(json_match)
            library["skills"] = skills
        except Exception as e:
            print(f"    ⚠️  技能生成失败：{e}")
            library["skills"] = []
        
        return library
    
    def _ai_generate_values(
        self,
        library: Dict[str, Any],
        research_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """AI 生成价值观"""
        prompt = f"""
基于以下研究资料，分析这个人物的价值观和思维框架。

要求：
1. 分析事业观、情感观、成长观、世界观
2. 描述问题分析方式、决策方式、沟通策略
3. 以 JSON 格式输出，格式如下：
{{
  "values": {{
    "事业观": "...",
    "情感观": "...",
    "成长观": "...",
    "世界观": "..."
  }},
  "thinking_framework": {{
    "问题分析": "...",
    "决策方式": "...",
    "沟通策略": "..."
  }}
}}

研究资料摘要：
{json.dumps(research_data, ensure_ascii=False, indent=2)[:2000]}

请直接输出 JSON 对象，不要其他内容。
"""
        
        try:
            response = self.ai_generator.generate_with_ai(prompt)
            json_match = response.strip()
            if json_match.startswith("```json"):
                json_match = json_match[7:-3]
            
            result = json.loads(json_match)
            library["values"] = result.get("values", library["values"])
            library["thinking_framework"] = result.get("thinking_framework", library["thinking_framework"])
        except Exception as e:
            print(f"    ⚠️  价值观生成失败：{e}")
        
        return library
    
    def _ai_generate_knowledge(
        self,
        library: Dict[str, Any],
        research_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """AI 生成知识领域"""
        prompt = f"""
基于以下研究资料，列出这个人物的知识领域和专业背景。

要求：
1. 列出 3-8 个知识领域
2. 每个领域用简短词语描述
3. 以 JSON 数组格式输出

研究资料摘要：
{json.dumps(research_data, ensure_ascii=False, indent=2)[:1000]}

请直接输出 JSON 数组，不要其他内容。
"""
        
        try:
            response = self.ai_generator.generate_with_ai(prompt)
            json_match = response.strip()
            if json_match.startswith("```json"):
                json_match = json_match[7:-3]
            
            knowledge_domains = json.loads(json_match)
            library["knowledge_domains"] = knowledge_domains
        except Exception as e:
            print(f"    ⚠️  知识领域生成失败：{e}")
            library["knowledge_domains"] = []
        
        return library
    
    def _generate_examples(
        self,
        person_name: str,
        library: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """生成对话示例"""
        examples = []
        
        # 基于技能生成示例
        for skill in library["skills"][:3]:  # 前 3 个技能
            example = {
                "scenario": f"展示{skill['name']}的场景",
                "dialogue": f"[示例对话基于{skill['description']}]",
                "analysis": f"体现了{skill['name']}",
            }
            examples.append(example)
        
        return examples
    
    def save_library(
        self,
        library: Dict[str, Any],
        output_dir: str,
        formats: List[str] = ["json", "md"],
    ) -> List[str]:
        """
        保存能力库
        
        Args:
            library: 能力库字典
            output_dir: 输出目录
            formats: 输出格式 (json, md)
        
        Returns:
            保存的文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        person_name = library["name"]
        
        # JSON 格式
        if "json" in formats:
            json_path = output_dir / f"{person_name}_能力库.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(library, f, ensure_ascii=False, indent=2)
            saved_files.append(str(json_path))
            print(f"  ✅ JSON 已保存：{json_path}")
        
        # Markdown 格式
        if "md" in formats:
            md_path = output_dir / f"{person_name}_能力库.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self._library_to_markdown(library))
            saved_files.append(str(md_path))
            print(f"  ✅ Markdown 已保存：{md_path}")
        
        return saved_files
    
    def _library_to_markdown(self, library: Dict[str, Any]) -> str:
        """将能力库转换为 Markdown"""
        md = f"# {library['name']} - 能力库\n\n"
        md += f"**版本:** {library['version']}\n"
        md += f"**更新时间:** {library['updated_at']}\n\n"
        
        md += "## 风格特征\n\n"
        md += f"- **语气:** {library['style']['tone']}\n"
        md += f"- **节奏:** {library['style']['pace'] or '未指定'}\n"
        md += f"- **方式:** {library['style']['approach'] or '未指定'}\n\n"
        
        md += "## 核心技能\n\n"
        for i, skill in enumerate(library['skills'], 1):
            md += f"### {i}. {skill['name']}\n\n"
            md += f"{skill['description']}\n\n"
            if skill.get('examples'):
                md += "**示例:**\n"
                for ex in skill['examples']:
                    md += f"- {ex}\n"
                md += "\n"
        
        md += "## 语言模式\n\n"
        for pattern_type, patterns in library['language_patterns'].items():
            if patterns:
                md += f"### {pattern_type}\n\n"
                for p in patterns[:10]:
                    md += f"- {p}\n"
                md += "\n"
        
        md += "## 价值观\n\n"
        for key, value in library['values'].items():
            if value:
                md += f"**{key}:** {value}\n\n"
        
        md += "## 思维框架\n\n"
        for key, value in library['thinking_framework'].items():
            if value:
                md += f"**{key}:** {value}\n\n"
        
        md += "## 知识领域\n\n"
        for domain in library['knowledge_domains']:
            md += f"- {domain}\n"
        
        if library.get('examples'):
            md += "\n## 对话示例\n\n"
            for ex in library['examples']:
                md += f"### {ex['scenario']}\n\n"
                md += f"{ex['dialogue']}\n\n"
                md += f"**分析:** {ex['analysis']}\n\n"
        
        return md


# ── 质量验证 ───────────────────────────────────────────────────


class QualityValidator:
    """能力库质量验证器"""
    
    @staticmethod
    def validate(library: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证能力库质量
        
        Args:
            library: 能力库字典
        
        Returns:
            验证结果
        """
        issues = []
        score = 100
        
        # 检查必填字段
        required_fields = ["name", "role", "style", "skills", "values"]
        for field in required_fields:
            if field not in library or not library[field]:
                issues.append(f"缺少必填字段：{field}")
                score -= 10
        
        # 检查技能数量
        skill_count = len(library.get("skills", []))
        if skill_count < 3:
            issues.append(f"技能数量不足（建议 3-6 个，当前：{skill_count}）")
            score -= 10
        elif skill_count > 8:
            issues.append(f"技能数量过多（建议 3-6 个，当前：{skill_count}）")
            score -= 5
        
        # 检查语言模式
        language_patterns = library.get("language_patterns", {})
        pattern_count = sum(len(v) for v in language_patterns.values())
        if pattern_count < 10:
            issues.append(f"语言模式不足（建议 10+ 条，当前：{pattern_count}）")
            score -= 10
        
        # 检查示例
        example_count = len(library.get("examples", []))
        if example_count < 3:
            issues.append(f"示例不足（建议 3+ 个，当前：{example_count}）")
            score -= 5
        
        # 检查完整性
        completeness = {
            "name": bool(library.get("name")),
            "role": bool(library.get("role")),
            "skills": len(library.get("skills", [])) >= 3,
            "language_patterns": pattern_count >= 10,
            "values": all(library.get("values", {}).values()),
            "examples": example_count >= 3,
        }
        
        return {
            "passed": score >= 60,
            "score": max(0, score),
            "issues": issues,
            "completeness": completeness,
            "suggestions": [
                "增加更多具体案例",
                "补充语言模式细节",
                "完善价值观描述",
            ] if score < 80 else [],
        }


# ── 完整自动化流程 ───────────────────────────────────────────────────


def auto_generate_ability_library(
    person_name: str,
    analysis_results: Dict[str, Any],
    research_data: Dict[str, Any],
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    自动化生成能力库完整流程
    
    Args:
        person_name: 人物姓名
        analysis_results: NLP 分析结果
        research_data: 研究数据
        output_dir: 输出目录
    
    Returns:
        生成结果
    """
    if output_dir is None:
        output_dir = f"./ability_libraries/{person_name}"
    
    print(f"\n🚀 开始自动生成 {person_name} 的能力库...")
    
    # 1. 生成能力库
    generator = AbilityLibraryGenerator()
    library = generator.generate_from_analysis(
        person_name=person_name,
        analysis_results=analysis_results,
        research_data=research_data,
    )
    
    # 2. 质量验证
    print("\n✅ 质量验证...")
    validation = QualityValidator.validate(library)
    
    print(f"  得分：{validation['score']}/100")
    if validation['issues']:
        print(f"  问题：{len(validation['issues'])} 个")
        for issue in validation['issues'][:5]:
            print(f"    - {issue}")
    
    # 3. 保存
    print("\n💾 保存能力库...")
    saved_files = generator.save_library(library, output_dir)
    
    # 4. 保存验证报告
    validation_path = Path(output_dir) / "quality_report.json"
    with open(validation_path, "w", encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)
    
    return {
        "person_name": person_name,
        "library": library,
        "validation": validation,
        "saved_files": saved_files,
        "generated_at": datetime.now().isoformat(),
    }


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="能力库自动生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从分析结果生成能力库
  python auto_generator.py generate --name "陈鲁豫" --analysis analysis.json --research research.json
  
  # 验证能力库质量
  python auto_generator.py validate library.json
  
  # 转换格式
  python auto_generator.py convert library.json -o output.md
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成能力库")
    gen_parser.add_argument("--name", required=True, help="人物姓名")
    gen_parser.add_argument("--analysis", required=True, help="NLP 分析结果文件")
    gen_parser.add_argument("--research", required=True, help="研究数据文件")
    gen_parser.add_argument("-o", "--output", help="输出目录")
    
    # validate 命令
    val_parser = subparsers.add_parser("validate", help="验证能力库质量")
    val_parser.add_argument("library", help="能力库 JSON 文件")
    
    # convert 命令
    conv_parser = subparsers.add_parser("convert", help="转换能力库格式")
    conv_parser.add_argument("input", help="输入 JSON 文件")
    conv_parser.add_argument("-o", "--output", required=True, help="输出文件")
    conv_parser.add_argument("--format", choices=["md", "json"], default="md", help="输出格式")
    
    args = parser.parse_args()
    
    try:
        if args.command == "generate":
            # 加载分析结果
            with open(args.analysis, "r", encoding="utf-8") as f:
                analysis_results = json.load(f)
            
            # 加载研究数据
            with open(args.research, "r", encoding="utf-8") as f:
                research_data = json.load(f)
            
            # 生成能力库
            result = auto_generate_ability_library(
                person_name=args.name,
                analysis_results=analysis_results,
                research_data=research_data,
                output_dir=args.output,
            )
            
            print(f"\n✅ 能力库生成完成！")
            print(f"  得分：{result['validation']['score']}/100")
            print(f"  文件：{', '.join(result['saved_files'])}")
        
        elif args.command == "validate":
            with open(args.library, "r", encoding="utf-8") as f:
                library = json.load(f)
            
            validation = QualityValidator.validate(library)
            
            print(f"\n📊 质量验证结果:")
            print(f"  得分：{validation['score']}/100")
            print(f"  通过：{'✅ 是' if validation['passed'] else '❌ 否'}")
            
            if validation['issues']:
                print(f"\n  问题:")
                for issue in validation['issues']:
                    print(f"    - {issue}")
        
        elif args.command == "convert":
            with open(args.input, "r", encoding="utf-8") as f:
                library = json.load(f)
            
            generator = AbilityLibraryGenerator()
            
            if args.format == "md":
                output_path = Path(args.output)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(generator._library_to_markdown(library))
                print(f"✅ Markdown 已保存：{output_path}")
            else:
                output_path = Path(args.output)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(library, f, ensure_ascii=False, indent=2)
                print(f"✅ JSON 已保存：{output_path}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
