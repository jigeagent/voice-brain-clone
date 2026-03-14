# 🚀 人物克隆快速指南

**v2.0 - 自动化版**

**3 分钟上手，15 分钟自动化生成，6 小时精品交付！**

---

## 📋 前置条件

### 必需
- [ ] OpenClaw 已安装
- [ ] Python 3.8+
- [ ] ffmpeg 已安装
- [ ] Noiz API key（https://developers.noiz.ai/api-keys）

### 可选（自动化功能）
- [ ] 通义千问 API key（用于 AI 生成能力库）
- [ ] yt-dlp（用于视频下载）
- [ ] jieba, nltk（用于中文分词）

### 可选（多平台支持）
- [ ] ElevenLabs API key（高质量声音克隆）
- [ ] Azure Speech API key（企业级 TTS）

---

## 🔧 快速配置

### 1. 安装依赖

```bash
# 进入技能目录
cd skills/voice-brain-clone

# 安装基础依赖
pip install requests beautifulsoup4 jieba nltk

# 安装视频下载工具
pip install yt-dlp
```

### 2. 配置 API Keys

```bash
# Noiz API（声音克隆）
python tts.py config --set-api-key YOUR_NOIZ_KEY

# 通义千问 API（AI 生成能力库）
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_KEY"

# ElevenLabs API（可选，高质量声音）
python platforms/elevenlabs.py config --set-api-key YOUR_ELEVENLABS_KEY

# Azure API（可选，企业级 TTS）
python platforms/azure_tts.py config --set-key YOUR_AZURE_KEY --region eastasia
```

### 3. 创建项目文件夹

```bash
mkdir clone-[人物名]
cd clone-[人物名]
mkdir audio research output config
```

---

## 🆕 v2.0 快速模式：一键自动化

**15 分钟生成初版能力库！**

```bash
# 一键完成：资料搜集 → 语言分析 → 能力库生成
python automation/auto_research.py research "陈鲁豫" -o ./research

# 合并文本并分析
cat ./research/陈鲁豫/baike/*.md > combined.txt
python automation/nlp_analyzer.py analyze combined.txt -o ./analysis

# AI 生成能力库
python automation/auto_generator.py generate \
  --name "陈鲁豫" \
  --analysis ./analysis.json \
  --research ./research/research_summary.json \
  -o ./ability_library
```

**输出：**
- `ability_library/陈鲁豫_能力库.json` - 结构化能力库
- `ability_library/陈鲁豫_能力库.md` - 可读版本
- `quality_report.json` - 质量评分（建议 80+ 分）

---

## 🎙️ 音色克隆（60 分钟）

### 步骤 1：准备参考音频

**要求：**
- 时长：30 秒以内
- 质量：清晰人声，无背景音乐
- 格式：WAV 或 MP3

**来源：**
- 采访视频（B 站/YouTube）
- 播客节目
- 公开演讲

### 步骤 2：截取音频

```bash
ffmpeg -i input.wav -t 30 -y ref-30s.wav
```

### 步骤 3：测试克隆

```bash
python tts.py -t "测试文本" --ref-audio ref-30s.wav -o test.mp3 --format mp3
```

### 步骤 4：验证效果

**播放 test.mp3，确认：**
- ✅ 音色相似度 90%+
- ✅ 无明显失真
- ✅ 语调自然

---

## 🧠 大脑克隆（180 分钟）

### 步骤 1：搜集资料（30 分钟）

**来源：**
- 百度百科/维基百科
- 采访视频（至少 3 个）
- 出版著作（如有）
- 媒体报道

### 步骤 2：分析语言模式（60 分钟）

**分析维度：**
- 常用词汇和短语
- 经典提问句式
- 口头禅
- 表达习惯

### 步骤 3：整理思维框架（60 分钟）

**整理内容：**
- 价值观（事业/情感/成长）
- 思维模式（问题分析/决策方式）
- 沟通策略

### 步骤 4：编写能力库（30 分钟）

**参考模板：** `research/陈鲁豫能力库.json`

---

## ✅ 整合验证（60 分钟）

### 验证清单

| 维度 | 标准 | 验证方法 |
|------|------|----------|
| 音色还原 | 90%+ | 听觉测试 |
| 语言风格 | 90%+ | 文本对比 |
| 思维模式 | 85%+ | 案例验证 |
| 价值观 | 90%+ | 资料对比 |

### 测试交流

**用克隆的风格进行 5 分钟测试对话，确认：**
- ✅ 音色自然
- ✅ 语言风格一致
- ✅ 思维逻辑连贯
- ✅ 价值观准确

---

## 📦 交付物

### 必需文件
- [ ] `能力库.json` - 结构化能力数据
- [ ] `交流指南.md` - 完整交流指南
- [ ] `快速参考卡.md` - 交流时快速查阅
- [ ] `voice-test.mp3` - 声音克隆测试

### 可选文件
- [ ] `研究总结.md` - 研究过程
- [ ] `使用手册.md` - 后续使用说明

---

## 💡 成功要素

### 音色克隆
- ✅ 参考音频质量高（清晰、无背景音）
- ✅ 截取片段有代表性（包含典型语调）
- ✅ API 调用参数合适（speed 0.9-1.0）

### 大脑克隆
- ✅ 资料来源多样（至少 3 个来源）
- ✅ 案例丰富（每技能 3-5 例）
- ✅ 可操作强（提供句式模板）

### 整合验证
- ✅ 测试对话真实场景
- ✅ 验证标准明确
- ✅ 反馈及时修正

---

## ⚠️ 注意事项

### 法律合规
- ✅ 仅使用公开资料
- ✅ 仅用于学习交流
- ❌ 不用于商业欺诈
- ❌ 不用于冒充真人

### 道德边界
- ✅ 明确告知是 AI 克隆
- ✅ 尊重肖像权
- ❌ 不用于敏感场景

---

## 📞 常见问题

### Q1: 参考音频超过 30 秒怎么办？
**A:** 用 ffmpeg 截取前 30 秒：
```bash
ffmpeg -i input.wav -t 30 -y ref-30s.wav
```

### Q2: 声音克隆效果不好？
**A:** 检查：
- 参考音频是否清晰
- 是否截取到代表性片段
- API key 是否有效

### Q3: 资料太少怎么办？
**A:** 优先保证质量：
- 聚焦核心技能（3-5 个）
- 每技能 1-2 个典型案例
- 标注资料限制

---

## 🎉 完成！

**现在你可以：**
1. 用克隆的声音进行语音交流
2. 用克隆的风格进行深度对话
3. 生成克隆的语音内容

**下一步：** 阅读《交流指南》，准备实战应用！

---

**祝你克隆成功！** 🚀
