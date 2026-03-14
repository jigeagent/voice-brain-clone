# 🔑 Voice-Brain-Clone API 配置管理方案

**版本:** v2.1.0  
**更新日期:** 2026-03-14 15:40  
**核心原则:** API 独立配置、灵活更换、企业自费

---

## 🎯 设计原则

### 1. API 独立配置 ✅
- 每个用户的 API key 独立存储
- 安装时引导用户配置自己的 API
- 支持运行时动态切换 API

### 2. 灵活更换 ✅
- 支持多账号切换
- 支持临时更换 API
- 支持环境变量覆盖

### 3. 企业自费 ✅
- 企业用户提供自己的 API key
- 企业版不包含任何 API 费用
- 支持配置多个 API 服务商

---

## 📋 API 配置方式（3 种）

### 方式 1: 安装时配置（推荐）

```bash
# 安装技能后自动引导配置
clawhub install voice-brain-clone

# 自动弹出配置向导
🔧 Voice-Brain-Clone 配置向导

请选择 TTS 平台：
1. Noiz（中文优化，性价比高）
2. ElevenLabs（高质量，业界最佳）
3. Azure TTS（企业级，情感丰富）
4. 暂不配置，稍后手动配置

请输入 API Key: ********
请确认 API Key: ********

✅ 配置成功！API Key 已保存到 ~/.voice-brain-clone/config.json
```

### 方式 2: 命令行配置

```bash
# 配置 Noiz API
python tts.py config --set-api-key YOUR_NOIZ_KEY

# 配置 ElevenLabs API
python platforms/elevenlabs.py config --set-api-key YOUR_ELEVENLABS_KEY

# 配置 Azure API
python platforms/azure_tts.py config --set-key YOUR_AZURE_KEY --region eastasia

# 查看当前配置
python tts.py config --show
```

### 方式 3: 环境变量配置

```bash
# Linux/macOS
export NOIZ_API_KEY="your_noiz_key"
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export AZURE_SPEECH_KEY="your_azure_key"

# Windows PowerShell
$env:NOIZ_API_KEY="your_noiz_key"
$env:ELEVENLABS_API_KEY="your_elevenlabs_key"
$env:AZURE_SPEECH_KEY="your_azure_key"

# .env 文件（推荐企业用户）
# 创建 .env 文件在项目根目录
NOIZ_API_KEY=your_noiz_key
ELEVENLABS_API_KEY=your_elevenlabs_key
AZURE_SPEECH_KEY=your_azure_key
```

---

## 🗂️ 配置文件结构

### 个人用户配置

**位置:** `~/.voice-brain-clone/config.json`

```json
{
  "version": "2.1.0",
  "user_type": "personal",
  "tts_platform": "noiz",
  "api_keys": {
    "noiz": "nk_xxxxxxxxxxxxxxxxxxxxxxxx",
    "elevenlabs": "xi_xxxxxxxxxxxxxxxxxxxxxxxx",
    "azure": {
      "key": "xxxxxxxxxxxxxxxxxxxxxxxx",
      "region": "eastasia"
    }
  },
  "default_platform": "noiz",
  "created_at": "2026-03-14T15:40:00+08:00",
  "updated_at": "2026-03-14T15:40:00+08:00"
}
```

### 企业用户配置

**位置:** `./enterprise/.env`

```bash
# 企业版配置文件
VOICE_BRAIN_VERSION=2.1.0
USER_TYPE=enterprise

# TTS 平台配置（企业自行提供）
NOIZ_API_KEY=enterprise_noiz_key
ELEVENLABS_API_KEY=enterprise_elevenlabs_key
AZURE_SPEECH_KEY=enterprise_azure_key
AZURE_REGION=eastasia

# 可选：多账号配置
NOIZ_API_KEY_BACKUP=backup_noiz_key
ELEVENLABS_ACCOUNT_2=second_elevenlabs_key

# 使用统计
DAILY_USAGE_LIMIT=1000
MONTHLY_BUDGET=5000
```

---

## 🔄 API 切换流程

### 运行时切换

```bash
# 查看当前 API
python tts.py config --show

# 当前使用：Noiz API (nk_xxxxxx)

# 切换到 ElevenLabs
python tts.py config --use-platform elevenlabs

# ✅ 已切换到 ElevenLabs API (xi_xxxxxx)

# 临时使用指定 API（单次命令）
python tts.py -t "测试文本" --api-key TEMP_KEY -o output.mp3
```

### 代码中切换

```python
# 方式 1: 使用配置文件
from voice_brain_clone import TTS

tts = TTS(platform="noiz")  # 从配置加载 Noiz API
audio = tts.speak("你好")

# 切换到 ElevenLabs
tts.switch_platform("elevenlabs")  # 从配置加载 ElevenLabs API
audio = tts.speak("Hello")

# 方式 2: 临时指定 API
tts = TTS(api_key="temp_key", platform="noiz")
audio = tts.speak("临时使用")
```

---

## 📊 多用户支持

### 个人用户

| 特性 | 说明 |
|------|------|
| **API 存储** | `~/.voice-brain-clone/config.json` |
| **API 费用** | 个人承担 |
| **切换方式** | 命令行/配置文件 |
| **多账号** | 支持（手动切换） |

### 企业用户

| 特性 | 说明 |
|------|------|
| **API 存储** | `./enterprise/.env` |
| **API 费用** | 企业自行承担 |
| **切换方式** | 配置文件/环境变量 |
| **多账号** | 支持（自动负载均衡） |

### ClawHub 平台用户

| 特性 | 说明 |
|------|------|
| **API 存储** | ClawHub 用户配置中心 |
| **API 费用** | 从 ClawHub 账户扣除 |
| **切换方式** | ClawHub Web 界面 |
| **多账号** | 支持（Web 界面管理） |

---

## 💰 费用说明

### 个人版

| 项目 | 费用 | 说明 |
|------|------|------|
| **技能使用** | 免费/¥199/月 | 免费版功能受限 |
| **Noiz API** | ¥0.01/秒 | 个人自行承担 |
| **ElevenLabs** | $0.30/分钟 | 个人自行承担 |
| **Azure TTS** | ¥0.015/千字符 | 个人自行承担 |

### 企业版

| 项目 | 费用 | 说明 |
|------|------|------|
| **技能使用** | ¥999/月 | 包含技术支持 |
| **API 费用** | 企业自行提供 | **不包含在技能费用中** |
| **定制开发** | 面议 | 根据需求报价 |
| **API 管理** | 免费 | 多账号管理工具 |

### ClawHub 平台版

| 项目 | 费用 | 说明 |
|------|------|------|
| **技能使用** | 从 ClawHub 账户扣除 | 按使用量计费 |
| **API 费用** | 从 ClawHub 账户扣除 | 统一结算 |
| **套餐优惠** | 有 | 批量购买优惠 |

---

## 🔒 安全与隐私

### API Key 存储

| 方式 | 安全性 | 说明 |
|------|--------|------|
| **配置文件** | ⭐⭐⭐⭐ | 文件权限 600，仅用户可读写 |
| **环境变量** | ⭐⭐⭐⭐⭐ | 不落地，进程内存中 |
| **.env 文件** | ⭐⭐⭐⭐ | .gitignore 忽略，不提交版本库 |

### 最佳实践

```bash
# ✅ 推荐：使用环境变量
export NOIZ_API_KEY="your_key"
python tts.py -t "文本" -o output.mp3

# ✅ 推荐：.env 文件（加入.gitignore）
# .env
NOIZ_API_KEY=your_key

# ❌ 不推荐：命令行明文传递
python tts.py --api-key "your_key"  # 会留在 bash history

# ❌ 不推荐：硬编码在代码中
api_key = "your_key"  # 会泄露到版本库
```

---

## 📋 安装配置流程

### 个人用户安装

```bash
# 1. 安装技能
clawhub install voice-brain-clone

# 2. 自动弹出配置向导
🔧 Voice-Brain-Clone 配置向导

请选择 TTS 平台：
1. Noiz（中文优化，性价比高）
2. ElevenLabs（高质量，业界最佳）
3. Azure TTS（企业级，情感丰富）
4. 暂不配置，稍后手动配置

选择 [1-4]: 1

请输入 Noiz API Key: ********
（获取 API Key: https://developers.noiz.ai/api-keys）

✅ 配置成功！

# 3. 测试配置
python tts.py -t "测试" -o test.mp3
✅ 语音生成成功！
```

### 企业用户安装

```bash
# 1. 下载企业版
git clone https://github.com/your-repo/voice-brain-clone-enterprise

# 2. 配置 API
cd voice-brain-clone-enterprise
cp .env.example .env

# 3. 编辑 .env 文件
# 填入企业自己的 API keys
NOIZ_API_KEY=enterprise_key
ELEVENLABS_API_KEY=enterprise_key
AZURE_SPEECH_KEY=enterprise_key

# 4. 测试
python tts.py -t "测试" -o test.mp3
✅ 企业版配置成功！
```

---

## 🎯 常见问题

### Q1: 可以更换 API 服务商吗？
**A:** ✅ 可以！随时更换，支持 Noiz/ElevenLabs/Azure 自由切换。

### Q2: 企业版包含 API 费用吗？
**A:** ❌ 不包含。企业版仅包含技能使用费，API 费用由企业自行承担和配置。

### Q3: 可以同时配置多个 API 吗？
**A:** ✅ 可以！支持多账号配置，自动负载均衡或手动切换。

### Q4: API Key 安全吗？
**A:** ✅ 安全！采用文件权限 600 保护，支持环境变量，不落地存储。

### Q5: 可以临时借用别人的 API 吗？
**A:** ✅ 可以！支持命令行临时指定 API key（单次有效）。

---

## 📞 技术支持

### 配置问题
- **文档:** `docs/API_CONFIG.md`
- **视频:** B 站搜索"Voice-Brain-Clone 配置教程"
- **社群:** 添加阿中微信获取技术支持

### API 申请
- **Noiz:** https://developers.noiz.ai/api-keys
- **ElevenLabs:** https://docs.elevenlabs.io/
- **Azure:** https://portal.azure.com/

---

**文档版本:** v2.1.0  
**最后更新:** 2026-03-14 15:40  
**责任人:** 阿中
