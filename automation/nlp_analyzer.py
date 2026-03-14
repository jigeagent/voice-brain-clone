#!/usr/bin/env python3
"""
NLP 语言分析工具 - 自动分析语言特征

功能：
- 词频统计
- 句式分析
- 情感分析
- 模式识别（常用词汇、经典句式、口头禅）

依赖：
- jieba (中文分词)
- nltk (英文处理)
- textblob (情感分析)
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Counter
from datetime import datetime
from collections import Counter

# 尝试导入中文分词
try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False
    print("⚠️  jieba 未安装，中文分析功能受限")
    print("安装：pip install jieba")

# 尝试导入英文处理
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    print("⚠️  nltk 未安装，英文分析功能受限")
    print("安装：pip install nltk")

# ── 文本预处理 ───────────────────────────────────────────────────


class TextPreprocessor:
    """文本预处理器"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 去除特殊字符（保留标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:，。！？；：""''""''（）()【】\[\]]', '', text)
        # 去除 URL
        text = re.sub(r'http[s]?://\S+', '', text)
        # 去除 @提及
        text = re.sub(r'@\w+', '', text)
        # 去除#话题#
        text = re.sub(r'#\w+#', '', text)
        
        return text.strip()
    
    @staticmethod
    def split_sentences(text: str, language: str = "zh") -> List[str]:
        """分句"""
        if language == "zh":
            # 中文分句
            sentences = re.split(r'[。！？.!?]', text)
        else:
            # 英文分句
            if HAS_NLTK:
                sentences = sent_tokenize(text)
            else:
                sentences = re.split(r'[.!?]', text)
        
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def tokenize(text: str, language: str = "zh") -> List[str]:
        """分词"""
        if language == "zh":
            if HAS_JIEBA:
                return list(jieba.cut(text))
            else:
                # 简单按字符分割
                return list(text)
        else:
            if HAS_NLTK:
                return word_tokenize(text)
            else:
                return text.split()
    
    @staticmethod
    def remove_stopwords(words: List[str], language: str = "zh") -> List[str]:
        """去除停用词"""
        # 中文停用词
        zh_stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
            '他', '她', '它', '们', '这个', '那个', '什么', '怎么', '可以',
        }
        
        # 英文停用词
        en_stopwords = {
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'can', 'just', 'don', 'now', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am',
        }
        
        stopwords = zh_stopwords if language == "zh" else en_stopwords
        
        return [w for w in words if w.lower() not in stopwords and len(w.strip()) > 0]


# ── 词频分析 ───────────────────────────────────────────────────


class WordFrequencyAnalyzer:
    """词频分析器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
        self.preprocessor = TextPreprocessor()
    
    def analyze(
        self,
        text: str,
        top_n: int = 50,
        min_length: int = 2,
        include_stopwords: bool = False,
    ) -> Dict[str, Any]:
        """
        分析词频
        
        Args:
            text: 输入文本
            top_n: 返回前 N 个高频词
            min_length: 最小词长
            include_stopwords: 是否包含停用词
        
        Returns:
            词频分析结果
        """
        # 清理文本
        text = self.preprocessor.clean_text(text)
        
        # 分词
        words = self.preprocessor.tokenize(text, self.language)
        
        # 过滤短词
        words = [w for w in words if len(w.strip()) >= min_length]
        
        # 去除停用词
        if not include_stopwords:
            words = self.preprocessor.remove_stopwords(words, self.language)
        
        # 统计词频
        word_counts = Counter(words)
        total_words = len(words)
        unique_words = len(word_counts)
        
        # 前 N 个高频词
        top_words = word_counts.most_common(top_n)
        
        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "top_words": [{"word": w, "count": c, "frequency": round(c / total_words * 100, 3)} for w, c in top_words],
            "word_cloud_data": dict(word_counts),  # 用于词云生成
        }


# ── 句式分析 ───────────────────────────────────────────────────


class SentencePatternAnalyzer:
    """句式分析器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
        self.preprocessor = TextPreprocessor()
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析句式模式
        
        Args:
            text: 输入文本
        
        Returns:
            句式分析结果
        """
        # 清理文本
        text = self.preprocessor.clean_text(text)
        
        # 分句
        sentences = self.preprocessor.split_sentences(text, self.language)
        
        # 分析句式
        patterns = {
            "question": [],  # 问句
            "exclamation": [],  # 感叹句
            "short": [],  # 短句 (<10 字)
            "medium": [],  # 中句 (10-30 字)
            "long": [],  # 长句 (>30 字)
            "parallel": [],  # 排比句
        }
        
        for sent in sentences:
            if not sent:
                continue
            
            # 问句
            if sent.endswith('?') or sent.endswith('？') or sent.startswith('怎么') or sent.startswith('什么'):
                patterns["question"].append(sent)
            
            # 感叹句
            if sent.endswith('!') or sent.endswith('！'):
                patterns["exclamation"].append(sent)
            
            # 按长度分类
            length = len(sent)
            if length < 10:
                patterns["short"].append(sent)
            elif length < 30:
                patterns["medium"].append(sent)
            else:
                patterns["long"].append(sent)
        
        # 检测排比句（简单规则：相似开头）
        sentence_starts = Counter([sent[:5] for sent in sentences if len(sent) > 5])
        for start, count in sentence_starts.items():
            if count >= 3:  # 3 个以上句子开头相似
                parallel_sents = [s for s in sentences if s.startswith(start)]
                patterns["parallel"].extend(parallel_sents)
        
        return {
            "total_sentences": len(sentences),
            "avg_sentence_length": round(sum(len(s) for s in sentences) / len(sentences), 2) if sentences else 0,
            "patterns": {
                "question_count": len(patterns["question"]),
                "exclamation_count": len(patterns["exclamation"]),
                "short_count": len(patterns["short"]),
                "medium_count": len(patterns["medium"]),
                "long_count": len(patterns["long"]),
                "parallel_count": len(patterns["parallel"]),
            },
            "examples": {
                "questions": patterns["question"][:5],
                "exclamations": patterns["exclamation"][:5],
                "short_sentences": patterns["short"][:5],
                "long_sentences": patterns["long"][:5],
                "parallel_sentences": patterns["parallel"][:5],
            },
        }


# ── 情感分析 ───────────────────────────────────────────────────


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self):
        try:
            from textblob import TextBlob
            self.has_textblob = True
        except ImportError:
            self.has_textblob = False
            print("⚠️  textblob 未安装，情感分析功能受限")
    
    def analyze(self, text: str, language: str = "zh") -> Dict[str, Any]:
        """
        分析情感
        
        Args:
            text: 输入文本
            language: 语言
        
        Returns:
            情感分析结果
        """
        # 简单情感词典（实际应该用更复杂的模型）
        positive_words = {
            '好', '棒', '优秀', '出色', '完美', '喜欢', '爱', '开心', '快乐',
            '幸福', '满意', '赞', '支持', '鼓励', '希望', '梦想', '成功',
            'good', 'great', 'excellent', 'perfect', 'love', 'like', 'happy',
            'wonderful', 'amazing', 'fantastic', 'awesome',
        }
        
        negative_words = {
            '坏', '差', '糟糕', '讨厌', '恨', '伤心', '难过', '失望',
            '失败', '错误', '问题', '困难', '痛苦', '悲伤', '愤怒',
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry',
            'disappointed', 'failed', 'wrong', 'problem',
        }
        
        # 分词
        words = TextPreprocessor.tokenize(text, language)
        
        # 统计情感词
        positive_count = sum(1 for w in words if w.lower() in positive_words)
        negative_count = sum(1 for w in words if w.lower() in negative_words)
        total = positive_count + negative_count
        
        # 计算情感得分
        if total > 0:
            sentiment_score = (positive_count - negative_count) / total
        else:
            sentiment_score = 0
        
        # 判断情感倾向
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 3),
            "positive_words_count": positive_count,
            "negative_words_count": negative_count,
            "emotional_words": {
                "positive": [w for w in words if w.lower() in positive_words][:10],
                "negative": [w for w in words if w.lower() in negative_words][:10],
            },
        }


# ── 口头禅识别 ───────────────────────────────────────────────────


class CatchphraseAnalyzer:
    """口头禅识别器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
    
    def analyze(self, text: str, min_length: int = 2, max_length: int = 10) -> Dict[str, Any]:
        """
        识别口头禅和常用表达
        
        Args:
            text: 输入文本
            min_length: 最短短语长度
            max_length: 最长短语长度
        
        Returns:
            口头禅分析结果
        """
        # 清理文本
        text = TextPreprocessor.clean_text(text)
        
        # 提取 n-gram
        catchphrases = {}
        
        for n in range(min_length, max_length + 1):
            # 滑动窗口提取 n-gram
            words = list(text) if self.language == "zh" else text.split()
            
            for i in range(len(words) - n + 1):
                phrase = ''.join(words[i:i+n]) if self.language == "zh" else ' '.join(words[i:i+n])
                
                # 过滤纯标点
                if re.match(r'^[\s\W]+$', phrase):
                    continue
                
                catchphrases[phrase] = catchphrases.get(phrase, 0) + 1
        
        # 筛选高频短语
        min_frequency = max(3, len(text) // 1000)  # 至少出现 3 次或每千字 1 次
        frequent_phrases = {
            phrase: count for phrase, count in catchphrases.items()
            if count >= min_frequency and len(phrase.strip()) >= min_length
        }
        
        # 排序
        sorted_phrases = sorted(frequent_phrases.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "catchphrases": [{"phrase": p, "count": c} for p, c in sorted_phrases[:30]],
            "total_unique_phrases": len(frequent_phrases),
        }


# ── 综合语言模式分析 ───────────────────────────────────────────────────


class LanguagePatternAnalyzer:
    """综合语言模式分析器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
        self.word_analyzer = WordFrequencyAnalyzer(language)
        self.sentence_analyzer = SentencePatternAnalyzer(language)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.catchphrase_analyzer = CatchphraseAnalyzer(language)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        综合分析语言模式
        
        Args:
            text: 输入文本
        
        Returns:
            综合分析结果
        """
        print("🔍 正在分析语言模式...")
        
        # 词频分析
        print("  - 词频统计...")
        word_freq = self.word_analyzer.analyze(text)
        
        # 句式分析
        print("  - 句式分析...")
        sentence_patterns = self.sentence_analyzer.analyze(text)
        
        # 情感分析
        print("  - 情感分析...")
        sentiment = self.sentiment_analyzer.analyze(text, self.language)
        
        # 口头禅识别
        print("  - 口头禅识别...")
        catchphrases = self.catchphrase_analyzer.analyze(text)
        
        return {
            "analyzed_at": datetime.now().isoformat(),
            "language": self.language,
            "text_length": len(text),
            "word_frequency": word_freq,
            "sentence_patterns": sentence_patterns,
            "sentiment": sentiment,
            "catchphrases": catchphrases,
            "summary": {
                "total_words": word_freq["total_words"],
                "unique_words": word_freq["unique_words"],
                "total_sentences": sentence_patterns["total_sentences"],
                "avg_sentence_length": sentence_patterns["avg_sentence_length"],
                "sentiment": sentiment["sentiment"],
                "top_catchphrases": [p["phrase"] for p in catchphrases["catchphrases"][:10]],
            },
        }
    
    def save_report(self, text: str, output_path: str) -> str:
        """
        保存分析报告
        
        Args:
            text: 输入文本
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        report = self.analyze(text)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON
        json_path = output_path.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存 Markdown 摘要
        md_path = output_path.with_suffix(".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 语言模式分析报告\n\n")
            f.write(f"分析时间：{report['analyzed_at']}\n")
            f.write(f"文本长度：{report['text_length']} 字\n\n")
            
            f.write(f"## 词汇统计\n\n")
            f.write(f"- 总词数：{report['word_frequency']['total_words']}\n")
            f.write(f"- 唯一词数：{report['word_frequency']['unique_words']}\n\n")
            
            f.write(f"## 高频词汇\n\n")
            for item in report['word_frequency']['top_words'][:20]:
                f.write(f"- {item['word']}: {item['count']} 次 ({item['frequency']}%)\n")
            f.write("\n")
            
            f.write(f"## 句式特征\n\n")
            patterns = report['sentence_patterns']['patterns']
            f.write(f"- 问句：{patterns['question_count']} 个\n")
            f.write(f"- 感叹句：{patterns['exclamation_count']} 个\n")
            f.write(f"- 短句：{patterns['short_count']} 个\n")
            f.write(f"- 长句：{patterns['long_count']} 个\n")
            f.write(f"- 平均句长：{report['sentence_patterns']['avg_sentence_length']} 字\n\n")
            
            f.write(f"## 情感倾向\n\n")
            f.write(f"- 情感：{report['sentiment']['sentiment']}\n")
            f.write(f"- 得分：{report['sentiment']['sentiment_score']}\n\n")
            
            f.write(f"## 口头禅/常用表达\n\n")
            for item in report['catchphrases']['catchphrases'][:15]:
                f.write(f"- {item['phrase']}: {item['count']} 次\n")
        
        print(f"✅ 报告已保存：{md_path}")
        return str(md_path)


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="NLP 语言分析工具 - 自动分析语言特征",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析文本文件
  python nlp_analyzer.py analyze input.txt -o report
  
  # 分析词频
  python nlp_analyzer.py word-freq input.txt --top 30
  
  # 分析句式
  python nlp_analyzer.py sentence-patterns input.txt
  
  # 识别口头禅
  python nlp_analyzer.py catchphrases input.txt
  
  # 情感分析
  python nlp_analyzer.py sentiment input.txt
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="综合分析")
    analyze_parser.add_argument("input", help="输入文本文件")
    analyze_parser.add_argument("-o", "--output", required=True, help="输出报告路径")
    analyze_parser.add_argument("--language", default="zh", help="语言")
    
    # word-freq 命令
    word_parser = subparsers.add_parser("word-freq", help="词频分析")
    word_parser.add_argument("input", help="输入文本文件")
    word_parser.add_argument("--top", type=int, default=50, help="前 N 个高频词")
    word_parser.add_argument("--language", default="zh", help="语言")
    
    # sentence-patterns 命令
    sentence_parser = subparsers.add_parser("sentence-patterns", help="句式分析")
    sentence_parser.add_argument("input", help="输入文本文件")
    sentence_parser.add_argument("--language", default="zh", help="语言")
    
    # catchphrases 命令
    catchphrase_parser = subparsers.add_parser("catchphrases", help="口头禅识别")
    catchphrase_parser.add_argument("input", help="输入文本文件")
    catchphrase_parser.add_argument("--language", default="zh", help="语言")
    
    # sentiment 命令
    sentiment_parser = subparsers.add_parser("sentiment", help="情感分析")
    sentiment_parser.add_argument("input", help="输入文本文件")
    sentiment_parser.add_argument("--language", default="zh", help="语言")
    
    args = parser.parse_args()
    
    try:
        # 读取输入文件
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        
        if args.command == "analyze":
            analyzer = LanguagePatternAnalyzer(language=args.language)
            report_path = analyzer.save_report(text, args.output)
        
        elif args.command == "word-freq":
            analyzer = WordFrequencyAnalyzer(language=args.language)
            result = analyzer.analyze(text, top_n=args.top)
            
            print(f"\n📊 词频统计 (前{args.top}个):")
            for item in result['top_words']:
                print(f"  {item['word']:20} {item['count']:5} 次 ({item['frequency']}%)")
        
        elif args.command == "sentence-patterns":
            analyzer = SentencePatternAnalyzer(language=args.language)
            result = analyzer.analyze(text)
            
            print(f"\n📊 句式分析:")
            print(f"  总句数：{result['total_sentences']}")
            print(f"  平均句长：{result['avg_sentence_length']} 字")
            print(f"  问句：{result['patterns']['question_count']} 个")
            print(f"  感叹句：{result['patterns']['exclamation_count']} 个")
            print(f"  短句：{result['patterns']['short_count']} 个")
            print(f"  长句：{result['patterns']['long_count']} 个")
        
        elif args.command == "catchphrases":
            analyzer = CatchphraseAnalyzer(language=args.language)
            result = analyzer.analyze(text)
            
            print(f"\n📊 口头禅/常用表达:")
            for item in result['catchphrases'][:20]:
                print(f"  {item['phrase']:30} {item['count']} 次")
        
        elif args.command == "sentiment":
            analyzer = SentimentAnalyzer()
            result = analyzer.analyze(text, language=args.language)
            
            print(f"\n📊 情感分析:")
            print(f"  情感倾向：{result['sentiment']}")
            print(f"  得分：{result['sentiment_score']}")
            print(f"  正面词：{result['emotional_words']['positive'][:10]}")
            print(f"  负面词：{result['emotional_words']['negative'][:10]}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
