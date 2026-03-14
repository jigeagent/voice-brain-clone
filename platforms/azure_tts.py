#!/usr/bin/env python3
"""
Azure Cognitive Services TTS 集成 - 企业级语音服务

功能：
- 自定义语音功能
- 情感控制
- 多语言支持
- 语音合成标记语言 (SSML)

API 文档：https://docs.microsoft.com/azure/cognitive-services/speech-service/
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# ── 配置 ───────────────────────────────────────────────────

AZURE_SPEECH_URL = "https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
AZURE_KEY_FILE = Path.home() / ".azure_speech_key"
AZURE_REGION_FILE = Path.home() / ".azure_speech_region"

# Azure 预设声音（中文）
AZURE_VOICES_CN = {
    "xiaoxiao": {
        "name": "晓晓",
        "voice": "zh-CN-XiaoxiaoNeural",
        "style": "general",
        "description": "温暖、亲切的女声",
    },
    "yunxi": {
        "name": "云希",
        "voice": "zh-CN-YunxiNeural",
        "style": "general",
        "description": "阳光、专业的男声",
    },
    "xiaoyi": {
        "name": "晓伊",
        "voice": "zh-CN-XiaoyiNeural",
        "style": "general",
        "description": "活泼、年轻的女声",
    },
    "yunyang": {
        "name": "云扬",
        "voice": "zh-CN-YunyangNeural",
        "style": "customerservice",
        "description": "专业、稳重的男声（适合客服）",
    },
}

# 情感风格
EMOTION_STYLES = {
    "neutral": "中性",
    "cheerful": "开心",
    "sad": "悲伤",
    "angry": "生气",
    "excited": "兴奋",
    "friendly": "友好",
    "terrified": "害怕",
    "shouting": "喊叫",
    "unfriendly": "不友好",
    "whispering": "耳语",
    "hopeful": "充满希望",
    "disgruntled": "不满",
    "serious": "严肃",
    "depressed": "沮丧",
    "envious": "嫉妒",
    "affectionate": "深情",
    "gentle": "温柔",
    "embarrassed": "尴尬",
    "anxious": "焦虑",
    "fearful": "恐惧",
    "grateful": "感激",
    "poetry-reading": "诗歌朗诵",
    "angry-sad": "悲伤的愤怒",
    "sad-angry": "愤怒的悲伤",
}

# ── API Key 管理 ───────────────────────────────────────────────────


def load_credentials() -> tuple:
    """加载 Azure 凭证"""
    key = os.environ.get("AZURE_SPEECH_KEY", "")
    region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
    
    if not key and AZURE_KEY_FILE.exists():
        key = AZURE_KEY_FILE.read_text(encoding="utf-8").strip()
    
    if not region and AZURE_REGION_FILE.exists():
        region = AZURE_REGION_FILE.read_text(encoding="utf-8").strip()
    
    return key, region


def save_credentials(key: str, region: str = "eastasia") -> None:
    """保存 Azure 凭证"""
    AZURE_KEY_FILE.write_text(key.strip(), encoding="utf-8")
    AZURE_REGION_FILE.write_text(region.strip(), encoding="utf-8")
    os.chmod(str(AZURE_KEY_FILE), 0o600)
    os.chmod(str(AZURE_REGION_FILE), 0o600)
    print(f"✅ Azure 凭证已保存 (Region: {region})")


def require_credentials() -> tuple:
    """获取凭证，如果不存在则报错"""
    key, region = load_credentials()
    if not key:
        raise RuntimeError(
            "❌ Azure Speech API key 未配置\n"
            "请设置环境变量 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION，或运行:\n"
            "  python azure_tts.py config --set-key YOUR_KEY --region eastasia"
        )
    return key, region


# ── SSML 生成器 ───────────────────────────────────────────────────


def generate_ssml(
    text: str,
    voice: str,
    emotion: Optional[str] = None,
    rate: str = "medium",
    pitch: str = "medium",
    volume: str = "medium",
    prosody_breaks: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    生成 SSML（语音合成标记语言）
    
    Args:
        text: 要转换的文本
        voice: 声音名称（如 zh-CN-XiaoxiaoNeural）
        emotion: 情感风格（见 EMOTION_STYLES）
        rate: 语速 (x-slow, slow, medium, fast, x-fast)
        pitch: 音调 (x-low, low, medium, high, x-high)
        volume: 音量 (silent, x-soft, soft, medium, loud, x-loud)
        prosody_breaks: 停顿列表 [{'time': '500ms'}, ...]
    
    Returns:
        SSML 字符串
    """
    # 基础 SSML
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="{voice}">'''
    
    # 添加情感风格
    if emotion and emotion in EMOTION_STYLES:
        ssml += f'<mstts:express-as style="{emotion}">'
    
    # 添加韵律设置
    ssml += f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">'
    
    # 处理文本和停顿
    if prosody_breaks:
        parts = text.split('\n')
        for i, part in enumerate(parts):
            ssml += part.strip()
            if i < len(prosody_breaks):
                break_time = prosody_breaks[i].get('time', '500ms')
                ssml += f'<break time="{break_time}"/>'
            if i < len(parts) - 1:
                ssml += '<break time="300ms"/>'
    else:
        ssml += text
    
    # 关闭标签
    ssml += '</prosody>'
    
    if emotion and emotion in EMOTION_STYLES:
        ssml += '</mstts:express-as>'
    
    ssml += '''</voice>
</speak>'''
    
    return ssml


# ── Azure TTS 客户端 ───────────────────────────────────────────────────


class AzureTTS:
    """Azure Cognitive Services TTS 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        self.api_key = api_key or require_credentials()[0]
        self.region = region or require_credentials()[1]
        self.url = AZURE_SPEECH_URL.format(region=self.region)
        
        self.session = requests.Session()
        self.session.headers.update({
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            "User-Agent": "VoiceBrainClone/1.0",
        })
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """获取可用声音列表"""
        url = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        emotion: Optional[str] = None,
        rate: str = "medium",
        pitch: str = "medium",
        volume: str = "medium",
        ssml: Optional[str] = None,
    ) -> str:
        """
        文本转语音
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
            voice: 声音名称
            emotion: 情感风格
            rate: 语速
            pitch: 音调
            volume: 音量
            ssml: 自定义 SSML（如果提供，其他参数忽略）
        
        Returns:
            output_path: 输出文件路径
        """
        # 生成或使用提供的 SSML
        if ssml:
            ssml_content = ssml
        else:
            ssml_content = generate_ssml(
                text=text,
                voice=voice,
                emotion=emotion,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
        
        # 发送请求
        resp = self.session.post(self.url, data=ssml_content.encode("utf-8"))
        resp.raise_for_status()
        
        # 保存音频文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(resp.content)
        
        print(f"✅ Azure 语音生成成功：{output_path}")
        return str(output_path)
    
    def synthesize_with_custom_voice(
        self,
        text: str,
        output_path: str,
        deployment_id: str,
        endpoint_id: str,
    ) -> str:
        """
        使用自定义语音（Custom Voice）
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
            deployment_id: 自定义语音部署 ID
            endpoint_id: 自定义语音端点 ID
        
        Returns:
            output_path: 输出文件路径
        """
        url = f"https://{self.region}.voice.speech.microsoft.com/cognitiveservices/v1"
        
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="{deployment_id}">
        {text}
    </voice>
</speak>'''
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            "User-Agent": "VoiceBrainClone/1.0",
        }
        
        resp = requests.post(url, headers=headers, data=ssml.encode("utf-8"))
        resp.raise_for_status()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(resp.content)
        
        print(f"✅ 自定义语音生成成功：{output_path}")
        return str(output_path)


# ── 语音配置模板 ───────────────────────────────────────────────────


def create_voice_profile(
    name: str,
    voice: str,
    emotion: str = "neutral",
    rate: str = "medium",
    pitch: str = "medium",
    volume: str = "medium",
    description: str = "",
) -> Dict[str, Any]:
    """创建语音配置模板"""
    return {
        "name": name,
        "voice": voice,
        "emotion": emotion,
        "rate": rate,
        "pitch": pitch,
        "volume": volume,
        "description": description,
        "created_at": datetime.now().isoformat(),
    }


def save_voice_profile(profile: Dict[str, Any], output_dir: str = "./voice_profiles") -> str:
    """保存语音配置模板到文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{profile['name'].replace(' ', '_')}.json"
    output_path = output_dir / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 语音配置已保存：{output_path}")
    return str(output_path)


def load_voice_profile(profile_path: str) -> Dict[str, Any]:
    """加载语音配置模板"""
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Azure TTS 集成 - 企业级语音服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 配置 API key
  python azure_tts.py config --set-key YOUR_KEY --region eastasia
  
  # 列出可用声音
  python azure_tts.py voices list
  
  # 使用预设声音生成
  python azure_tts.py speak -t "你好世界" -o output.mp3 --voice xiaoxiao
  
  # 使用情感生成
  python azure_tts.py speak -t "太棒了！" -o output.mp3 --voice xiaoxiao --emotion cheerful
  
  # 自定义语速音调
  python azure_tts.py speak -t "慢慢说" -o output.mp3 --rate slow --pitch low
  
  # 使用语音配置模板
  python azure_tts.py speak -t "文本" -o output.mp3 --profile ./profiles/narrator.json
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置 Azure 凭证")
    config_parser.add_argument("--set-key", dest="api_key", help="设置 API key")
    config_parser.add_argument("--region", default="eastasia", help="Azure 区域")
    
    # voices 命令
    voices_parser = subparsers.add_parser("voices", help="声音管理")
    voices_subparsers = voices_parser.add_subparsers(dest="voices_command")
    
    # voices list
    voices_list = voices_subparsers.add_parser("list", help="列出可用声音")
    voices_list.add_argument("--filter", help="过滤（如 zh-CN）")
    
    # profiles 命令
    profiles_parser = subparsers.add_parser("profiles", help="语音配置模板管理")
    profiles_subparsers = profiles_parser.add_subparsers(dest="profiles_command")
    
    # profiles create
    profiles_create = profiles_subparsers.add_parser("create", help="创建语音配置")
    profiles_create.add_argument("--name", required=True, help="配置名称")
    profiles_create.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="声音")
    profiles_create.add_argument("--emotion", default="neutral", help="情感风格")
    profiles_create.add_argument("--rate", default="medium", help="语速")
    profiles_create.add_argument("--pitch", default="medium", help="音调")
    profiles_create.add_argument("--volume", default="medium", help="音量")
    profiles_create.add_argument("--description", default="", help="描述")
    
    # speak 命令
    speak_parser = subparsers.add_parser("speak", help="生成语音")
    speak_parser.add_argument("-t", "--text", required=True, help="要转换的文本")
    speak_parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    speak_parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="声音")
    speak_parser.add_argument("--emotion", help="情感风格")
    speak_parser.add_argument("--rate", default="medium", help="语速")
    speak_parser.add_argument("--pitch", default="medium", help="音调")
    speak_parser.add_argument("--volume", default="medium", help="音量")
    speak_parser.add_argument("--profile", help="语音配置文件路径")
    
    args = parser.parse_args()
    
    try:
        if args.command == "config":
            if args.api_key:
                save_credentials(args.api_key, args.region)
            else:
                key, region = load_credentials()
                if key:
                    print(f"当前 API key: {key[:8]}...{key[-4:]}")
                    print(f"Region: {region}")
                else:
                    print("未配置 API key")
        
        elif args.command == "voices":
            if args.voices_command == "list":
                azure = AzureTTS()
                voices = azure.list_voices()
                
                if args.filter:
                    voices = [v for v in voices if args.filter in v.get("locale", "")]
                
                print(f"\n可用声音 ({len(voices)} 个):")
                print("-" * 80)
                for v in voices:
                    print(f"  {v['shortName']:40} {v.get('gender', ''):10} {v.get('locale', '')}")
        
        elif args.command == "profiles":
            if args.profiles_command == "create":
                profile = create_voice_profile(
                    name=args.name,
                    voice=args.voice,
                    emotion=args.emotion,
                    rate=args.rate,
                    pitch=args.pitch,
                    volume=args.volume,
                    description=args.description,
                )
                save_voice_profile(profile)
        
        elif args.command == "speak":
            # 加载配置文件或使用命令行参数
            if args.profile:
                profile = load_voice_profile(args.profile)
                voice = profile["voice"]
                emotion = profile.get("emotion")
                rate = profile.get("rate", "medium")
                pitch = profile.get("pitch", "medium")
                volume = profile.get("volume", "medium")
                print(f"使用语音配置：{profile['name']}")
            else:
                voice = args.voice
                emotion = args.emotion
                rate = args.rate
                pitch = args.pitch
                volume = args.volume
            
            azure = AzureTTS()
            output_path = azure.text_to_speech(
                text=args.text,
                output_path=args.output,
                voice=voice,
                emotion=emotion,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
            print(f"✅ 语音已生成：{output_path}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
