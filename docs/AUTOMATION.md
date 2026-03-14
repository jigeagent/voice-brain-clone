# 自动化功能说明

**更新时间：** 2026-03-12  
**版本：** 1.0

---

## 📋 功能总览

Voice-Brain-Clone 的自动化功能包括：

1. **自动资料搜集** (`auto_research.py`)
2. **自动语言分析** (`nlp_analyzer.py`)
3. **自动能力库生成** (`auto_generator.py`)

---

## 🔄 完整自动化流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    一键自动化流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 输入人物姓名                                                 │
│         ↓                                                       │
│  2. 自动搜集资料（百科、维基、新闻、视频）                       │
│         ↓                                                       │
│  3. 自动分析语言模式（词频、句式、情感、口头禅）                 │
│         ↓                                                       │
│  4. AI 自动生成能力库（技能、价值观、思维框架）                  │
│         ↓                                                       │
│  5. 质量验证与优化                                               │
│         ↓                                                       │
│  6. 输出完整能力库（JSON + Markdown）                            │
│                                                                 │
│  预计耗时：15-30 分钟（取决于资料丰富度）                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 自动资料搜集

**工具：** `automation/auto_research.py`

### 功能

- ✅ 自动搜索百度百科
- ✅ 自动搜索维基百科
- ✅ 自动搜索新闻采访
- ✅ 自动下载 B 站/YouTube 视频
- ✅ 自动提取音频

### 使用方法

#### 一键研究一个人物

```bash
python automation/auto_research.py research "陈鲁豫" -o ./research/陈鲁豫
```

**输出：**
```
research/陈鲁豫/
├── baike/
│   └── 陈鲁豫.md          # 百度百科内容
├── wikipedia/
│   └── 陈鲁豫.md          # 维基百科内容
├── news/
│   └── 陈鲁豫_news.json   # 新闻列表
├── videos/
│   └── [视频文件]         # 下载的视频
└── research_summary.json  # 汇总报告
```

#### 单独下载视频

```bash
# B 站视频
python automation/auto_research.py download-bilibili https://www.bilibili.com/video/BV1xx -o ./videos

# YouTube 视频
python automation/auto_research.py download-youtube https://www.youtube.com/watch?v=xxx -o ./videos
```

#### 提取音频

```bash
python automation/auto_research.py extract-audio video.mp4 -o audio.wav
```

#### 搜索新闻

```bash
python automation/auto_research.py search-news "陈鲁豫 采访" --limit 30 -o ./news
```

### 依赖安装

```bash
pip install requests beautifulsoup4 yt-dlp
```

---

## 2️⃣ 自动语言分析

**工具：** `automation/nlp_analyzer.py`

### 功能

- ✅ 词频统计（前 50 个高频词）
- ✅ 句式分析（问句、感叹句、长短句）
- ✅ 情感分析（积极/消极/中性）
- ✅ 口头禅识别（自动发现常用表达）
- ✅ 语言模式总结

### 使用方法

#### 综合分析

```bash
python automation/nlp_analyzer.py analyze ./research/陈鲁豫/采访文本.txt -o ./analysis/陈鲁豫_语言分析
```

**输出：**
- `陈鲁豫_语言分析.json` - 详细分析数据
- `陈鲁豫_语言分析.md` - 可读报告

#### 单独分析

```bash
# 词频统计
python automation/nlp_analyzer.py word-freq 文本.txt --top 30

# 句式分析
python automation/nlp_analyzer.py sentence-patterns 文本.txt

# 口头禅识别
python automation/nlp_analyzer.py catchphrases 文本.txt

# 情感分析
python automation/nlp_analyzer.py sentiment 文本.txt
```

### 分析结果示例

**词频统计：**
```
总词数：12,453
唯一词数：3,245

前 10 个高频词:
  - 问题                 234 次 (1.88%)
  - 觉得                 189 次 (1.52%)
  - 其实                 167 次 (1.34%)
  - 可能                 145 次 (1.16%)
  - 非常                 132 次 (1.06%)
  ...
```

**句式特征：**
```
总句数：856
平均句长：14.5 字
问句：123 个
感叹句：45 个
短句（<10 字）：234 个
长句（>30 字）：67 个
```

**口头禅识别：**
```
  - 对不对                 89 次
  - 我觉得                 76 次
  - 其实                   65 次
  - 怎么说呢               54 次
  - 你明白吗               43 次
```

**情感倾向：**
```
情感：积极
得分：0.35
正面词：['喜欢', '享受', '快乐', '幸福', '成长']
负面词：['困难', '挑战', '压力']
```

### 依赖安装

```bash
pip install jieba nltk textblob
```

---

## 3️⃣ 自动能力库生成

**工具：** `automation/auto_generator.py`

### 功能

- ✅ 基于分析结果自动生成能力库
- ✅ AI 生成技能描述
- ✅ AI 生成价值观和思维框架
- ✅ AI 生成对话示例
- ✅ 质量验证（自动评分）
- ✅ 多格式输出（JSON + Markdown）

### 使用方法

#### 一键生成能力库

```bash
python automation/auto_generator.py generate \
  --name "陈鲁豫" \
  --analysis ./analysis/陈鲁豫_语言分析.json \
  --research ./research/陈鲁豫/research_summary.json \
  -o ./ability_libraries/陈鲁豫
```

**输出：**
```
ability_libraries/陈鲁豫/
├── 陈鲁豫_能力库.json      # 结构化数据
├── 陈鲁豫_能力库.md        # 可读版本
└── quality_report.json     # 质量验证报告
```

#### 验证能力库质量

```bash
python automation/auto_generator.py validate 陈鲁豫_能力库.json
```

**输出示例：**
```
📊 质量验证结果:
  得分：85/100
  通过：✅ 是

  问题:
    - 示例不足（建议 3+ 个，当前：2）
```

#### 转换格式

```bash
# JSON 转 Markdown
python automation/auto_generator.py convert 陈鲁豫_能力库.json -o 陈鲁豫_能力库.md --format md

# Markdown 转 JSON
python automation/auto_generator.py convert 陈鲁豫_能力库.md -o 陈鲁豫_能力库.json --format json
```

### 生成的能力库结构

```json
{
  "name": "陈鲁豫",
  "role": "著名主持人、媒体人",
  "version": "1.0",
  "style": {
    "tone": "温和、亲切、善于倾听",
    "pace": "中等偏慢",
    "approach": "访谈式、引导式"
  },
  "skills": [
    {
      "name": "深度提问",
      "description": "通过层层递进的提问，引导嘉宾深入思考",
      "examples": [
        "你当时为什么会做出那个决定？",
        "这个选择对你来说意味着什么？"
      ]
    },
    {
      "name": "情感共鸣",
      "description": "快速与嘉宾建立情感连接，营造信任氛围",
      "examples": [
        "我能理解你当时的感受",
        "这确实很不容易"
      ]
    }
  ],
  "language_patterns": {
    "常用开场": ["你好，欢迎来这里", "今天想和你聊聊..."],
    "常用追问": ["为什么？", "能详细说说吗？", "当时是什么感觉？"],
    "常用回应": ["嗯嗯", "我明白", "这很有意思"],
    "常用总结": ["所以你的意思是...", "总的来说..."],
    "口头禅": ["对不对", "我觉得", "其实", "怎么说呢"]
  },
  "values": {
    "事业观": "真诚对待每一个采访对象，用心倾听每一个故事",
    "情感观": "情感需要表达，更需要理解",
    "成长观": "每一次挑战都是成长的机会"
  },
  "thinking_framework": {
    "问题分析": "从表面现象深入到底层动机",
    "决策方式": "综合考虑情感与理性",
    "沟通策略": "先建立信任，再深入交流"
  },
  "examples": [
    {
      "scenario": "嘉宾谈到困难经历",
      "dialogue": "那段时光一定很不容易吧？你是怎么走过来的？",
      "analysis": "体现情感共鸣和深度提问技能"
    }
  ]
}
```

### 依赖安装

```bash
pip install requests
```

**需要配置 AI API：**
```bash
export DASHSCOPE_API_KEY="your_qwen_api_key"
```

---

## 🚀 一键自动化脚本

创建 `run_full_automation.sh`：

```bash
#!/bin/bash

# 一键自动化：从人物姓名到完整能力库

PERSON_NAME=$1

if [ -z "$PERSON_NAME" ]; then
    echo "用法：./run_full_automation.sh 人物姓名"
    exit 1
fi

echo "🚀 开始自动化流程：$PERSON_NAME"

# 1. 资料搜集
echo "📚 步骤 1/3: 搜集资料..."
python automation/auto_research.py research "$PERSON_NAME" -o "./research/$PERSON_NAME"

# 2. 合并所有文本
echo "📝 步骤 2/3: 分析语言模式..."
cat ./research/$PERSON_NAME/baike/*.md > "./research/$PERSON_NAME/combined.txt"
cat ./research/$PERSON_NAME/wikipedia/*.md >> "./research/$PERSON_NAME/combined.txt"

python automation/nlp_analyzer.py analyze "./research/$PERSON_NAME/combined.txt" -o "./analysis/$PERSON_NAME"

# 3. 生成能力库
echo "🤖 步骤 3/3: 生成能力库..."
python automation/auto_generator.py generate \
  --name "$PERSON_NAME" \
  --analysis "./analysis/$PERSON_NAME.json" \
  --research "./research/$PERSON_NAME/research_summary.json" \
  -o "./ability_libraries/$PERSON_NAME"

echo "✅ 自动化流程完成！"
echo "能力库位置：./ability_libraries/$PERSON_NAME/"
```

**使用方法：**
```bash
chmod +x run_full_automation.sh
./run_full_automation.sh "陈鲁豫"
```

---

## 📊 自动化 vs 手动

| 维度 | 自动化 | 手动 |
|------|-------|------|
| **时间** | 15-30 分钟 | 4-6 小时 |
| **还原度** | 70-85% | 90%+ |
| **成本** | 低（API 费用） | 高（人工） |
| **一致性** | 高（标准化） | 中（依赖人员） |
| **适用场景** | 快速原型、批量生产 | 高质量交付、精品项目 |

**建议：**
- 先用自动化快速生成初版
- 再人工优化关键部分
- 平衡效率与质量

---

## 🎯 最佳实践

### 1. 资料质量控制

```bash
# 检查搜集的资料是否充分
ls -lh ./research/$PERSON_NAME/

# 如果百科内容太少，手动补充
# 如果视频太多，选择最有代表性的 3-5 个
```

### 2. 分析参数调优

```bash
# 对于正式演讲文本，增加最小词长
python nlp_analyzer.py word-freq 文本.txt --top 50 --min-length 3

# 对于对话文本，重点关注问句
python nlp_analyzer.py sentence-patterns 文本.txt
```

### 3. 能力库迭代

```bash
# 第 1 版：自动化生成
python auto_generator.py generate ...

# 第 2 版：人工审核 + 修改 JSON

# 第 3 版：重新生成 Markdown
python auto_generator.py convert library.json -o library.md
```

### 4. 批量处理

```bash
# 批量生成多个人物的能力库
for name in "人物 1" "人物 2" "人物 3"; do
    ./run_full_automation.sh "$name"
done
```

---

## ⚠️ 注意事项

### 1. API 配额限制

- Noiz: 免费层有限额
- 通义千问：需要 API key
- 注意控制调用频率

### 2. 版权与合规

- 仅使用公开资料
- 仅用于学习交流
- 不用于商业欺诈
- 尊重肖像权和名誉权

### 3. 质量验证

- 自动化生成的能力库需要人工审核
- 关键信息需要交叉验证
- 避免 AI 幻觉（编造事实）

---

## 📞 故障排除

### 问题 1: 视频下载失败

```bash
# 更新 yt-dlp
pip install -U yt-dlp

# 检查网络
ping www.bilibili.com
```

### 问题 2: 中文分词失败

```bash
# 安装 jieba
pip install jieba

# 检查导入
python -c "import jieba; print(jieba.cut('测试'))"
```

### 问题 3: AI 生成失败

```bash
# 检查 API key
echo $DASHSCOPE_API_KEY

# 测试 API
curl -X POST "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","input":{"messages":[{"role":"user","content":"你好"}]}}'
```

---

**持续更新中...**
