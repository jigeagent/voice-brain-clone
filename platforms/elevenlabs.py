#!/usr/bin/env python3
"""
ElevenLabs TTS 集成 - 高质量声音克隆

功能：
- API 集成
- 声音配置模板
- 声音克隆
- 与 Noiz 对比测试

API 文档：https://docs.elevenlabs.io/
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

# ── 配置 ───────────────────────────────────────────────────

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"
ELEVENLABS_KEY_FILE = Path.home() / ".elevenlabs_api_key"

# 预设声音配置模板
VOICE_TEMPLATES = {
    "professional_male": {
        "name": "专业男声",
        "voice_id": "pNInz6obLzXCQmrhxA9t",  # Adam (预定义声音)
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True,
    },
    "warm_female": {
        "name": "温暖女声",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella (预定义声音)
        "stability": 0.70,
        "similarity_boost": 0.80,
        "style": 0.0,
        "use_speaker_boost": True,
    },
    "narrator": {
        "name": "叙述者",
        "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold (预定义声音)
        "stability": 0.80,
        "similarity_boost": 0.70,
        "style": 0.0,
        "use_speaker_boost": True,
    },
}

# ── API Key 管理 ───────────────────────────────────────────────────


def load_api_key() -> Optional[str]:
    """从文件或环境变量加载 API key"""
    env_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if env_key:
        return env_key.strip()
    
    if ELEVENLABS_KEY_FILE.exists():
        return ELEVENLABS_KEY_FILE.read_text(encoding="utf-8").strip()
    
    return None


def save_api_key(key: str) -> None:
    """保存 API key 到文件"""
    ELEVENLABS_KEY_FILE.write_text(key.strip(), encoding="utf-8")
    os.chmod(str(ELEVENLABS_KEY_FILE), 0o600)
    print(f"✅ ElevenLabs API key 已保存")


def require_api_key() -> str:
    """获取 API key，如果不存在则报错"""
    key = load_api_key()
    if not key:
        raise RuntimeError(
            "❌ ElevenLabs API key 未配置\n"
            "请设置环境变量 ELEVENLABS_API_KEY 或运行:\n"
            "  python elevenlabs.py config --set-api-key YOUR_KEY"
        )
    return key


# ── 声音克隆核心功能 ───────────────────────────────────────────────────


class ElevenLabsTTS:
    """ElevenLabs TTS 客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or require_api_key()
        self.session = requests.Session()
        self.session.headers.update({
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        })
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """获取可用声音列表"""
        url = f"{ELEVENLABS_API_URL}/voices"
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("voices", [])
    
    def add_voice(
        self,
        name: str,
        audio_files: List[str],
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        添加克隆声音（Instant Voice Cloning）
        
        Args:
            name: 声音名称
            audio_files: 参考音频文件路径列表（WAV/MP3，建议 1-5 分钟）
            description: 声音描述
            labels: 标签（如 {"accent": "chinese", "age": "middle-aged"}）
        
        Returns:
            voice_id: 克隆声音的 ID
        """
        url = f"{ELEVENLABS_API_URL}/voices/add"
        
        files = []
        for audio_path in audio_files:
            files.append((
                "files",
                (Path(audio_path).name, open(audio_path, "rb"), "audio/mpeg"),
            ))
        
        data = {
            "name": name,
            "description": description,
            "labels": json.dumps(labels or {}),
        }
        
        resp = self.session.post(url, files=files, data=data)
        resp.raise_for_status()
        result = resp.json()
        
        # 关闭文件
        for _, (_, file_obj, _) in files:
            file_obj.close()
        
        voice_id = result.get("voice_id")
        print(f"✅ 声音克隆成功: {name} (ID: {voice_id})")
        return voice_id
    
    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        stability: float = 0.75,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        model_id: str = "eleven_monolingual_v1",
    ) -> str:
        """
        文本转语音
        
        Args:
            text: 要转换的文本
            voice_id: 声音 ID（预定义或克隆的）
            output_path: 输出音频文件路径
            stability: 稳定性 (0-1)，越高越稳定但越单调
            similarity_boost: 相似度增强 (0-1)，越高越像原声
            style: 风格夸张度 (0-1)，仅部分模型支持
            use_speaker_boost: 使用说话人增强
            model_id: 模型 ID
        
        Returns:
            output_path: 输出文件路径
        """
        url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
            },
        }
        
        resp = self.session.post(url, json=payload, stream=True)
        resp.raise_for_status()
        
        # 保存音频文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 语音生成成功: {output_path}")
        return str(output_path)
    
    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """获取声音详细信息"""
        url = f"{ELEVENLABS_API_URL}/voices/{voice_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    def delete_voice(self, voice_id: str) -> bool:
        """删除克隆的声音"""
        url = f"{ELEVENLABS_API_URL}/voices/{voice_id}"
        resp = self.session.delete(url)
        resp.raise_for_status()
        print(f"✅ 声音已删除: {voice_id}")
        return True


# ── 与 Noiz 对比测试 ───────────────────────────────────────────────────


def compare_with_noiz(
    text: str,
    elevenlabs_voice_id: str,
    noiz_ref_audio: str,
    output_dir: str = "./comparison",
) -> Dict[str, str]:
    """
    对比 ElevenLabs 和 Noiz 的生成效果
    
    Args:
        text: 测试文本
        elevenlabs_voice_id: ElevenLabs 声音 ID
        noiz_ref_audio: Noiz 参考音频路径
        output_dir: 输出目录
    
    Returns:
        结果文件路径字典
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # ElevenLabs 生成
    print("\n🎙️  正在使用 ElevenLabs 生成...")
    elevenlabs = ElevenLabsTTS()
    results["elevenlabs"] = elevenlabs.text_to_speech(
        text=text,
        voice_id=elevenlabs_voice_id,
        output_path=str(output_dir / "elevenlabs_output.mp3"),
    )
    
    # Noiz 生成（调用现有脚本）
    print("\n🎙️  正在使用 Noiz 生成...")
    noiz_script = Path(__file__).parent.parent.parent / "noizai-tts" / "scripts" / "tts.py"
    noiz_output = output_dir / "noiz_output.mp3"
    
    import subprocess
    cmd = [
        sys.executable, str(noiz_script),
        "-t", text,
        "--ref-audio", noiz_ref_audio,
        "-o", str(noiz_output),
        "--format", "mp3",
    ]
    subprocess.run(cmd, check=True)
    results["noiz"] = str(noiz_output)
    
    print(f"\n✅ 对比测试完成！")
    print(f"  ElevenLabs: {results['elevenlabs']}")
    print(f"  Noiz:       {results['noiz']}")
    
    return results


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="ElevenLabs TTS 集成 - 高质量声音克隆",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 配置 API key
  python elevenlabs.py config --set-api-key YOUR_KEY
  
  # 列出可用声音
  python elevenlabs.py voices list
  
  # 克隆新声音
  python elevenlabs.py voices clone --name "我的声音" --audio ref1.wav ref2.wav
  
  # 生成语音
  python elevenlabs.py speak -t "你好世界" --voice-id YOUR_VOICE_ID -o output.mp3
  
  # 使用预设模板
  python elevenlabs.py speak -t "你好" --template professional_male -o output.mp3
  
  # 与 Noiz 对比测试
  python elevenlabs.py compare --eleven-voice-id XXX --noiz-audio ref.wav -t "测试文本"
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置 API key")
    config_parser.add_argument("--set-api-key", dest="api_key", help="设置 API key")
    
    # voices 命令
    voices_parser = subparsers.add_parser("voices", help="声音管理")
    voices_subparsers = voices_parser.add_subparsers(dest="voices_command")
    
    # voices list
    voices_list = voices_subparsers.add_parser("list", help="列出可用声音")
    
    # voices clone
    voices_clone = voices_subparsers.add_parser("clone", help="克隆新声音")
    voices_clone.add_argument("--name", required=True, help="声音名称")
    voices_clone.add_argument("--audio", nargs="+", required=True, help="参考音频文件")
    voices_clone.add_argument("--description", default="", help="声音描述")
    
    # speak 命令
    speak_parser = subparsers.add_parser("speak", help="生成语音")
    speak_parser.add_argument("-t", "--text", required=True, help="要转换的文本")
    speak_parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    speak_parser.add_argument("--voice-id", help="声音 ID")
    speak_parser.add_argument("--template", choices=list(VOICE_TEMPLATES.keys()), help="使用预设模板")
    speak_parser.add_argument("--stability", type=float, default=0.75, help="稳定性 (0-1)")
    speak_parser.add_argument("--similarity-boost", type=float, default=0.75, help="相似度增强 (0-1)")
    
    # compare 命令
    compare_parser = subparsers.add_parser("compare", help="与 Noiz 对比测试")
    compare_parser.add_argument("--eleven-voice-id", required=True, help="ElevenLabs 声音 ID")
    compare_parser.add_argument("--noiz-audio", required=True, help="Noiz 参考音频")
    compare_parser.add_argument("-t", "--text", required=True, help="测试文本")
    compare_parser.add_argument("--output-dir", default="./comparison", help="输出目录")
    
    args = parser.parse_args()
    
    # 导入 sys 用于 compare 命令
    global sys
    import sys
    
    try:
        if args.command == "config":
            if args.api_key:
                save_api_key(args.api_key)
            else:
                key = load_api_key()
                if key:
                    print(f"当前 API key: {key[:8]}...{key[-4:]}")
                else:
                    print("未配置 API key")
        
        elif args.command == "voices":
            elevenlabs = ElevenLabsTTS()
            
            if args.voices_command == "list":
                voices = elevenlabs.get_voices()
                print(f"\n可用声音 ({len(voices)} 个):")
                print("-" * 60)
                for v in voices:
                    print(f"  {v['name']:30} ID: {v['voice_id']}")
                    if 'labels' in v:
                        print(f"    标签: {v['labels']}")
            
            elif args.voices_command == "clone":
                voice_id = elevenlabs.add_voice(
                    name=args.name,
                    audio_files=args.audio,
                    description=args.description,
                )
                print(f"克隆成功！Voice ID: {voice_id}")
        
        elif args.command == "speak":
            elevenlabs = ElevenLabsTTS()
            
            # 确定使用哪个声音
            if args.template:
                template = VOICE_TEMPLATES[args.template]
                voice_id = template["voice_id"]
                stability = template["stability"]
                similarity_boost = template["similarity_boost"]
                print(f"使用预设模板: {template['name']}")
            elif args.voice_id:
                voice_id = args.voice_id
                stability = args.stability
                similarity_boost = args.similarity_boost
            else:
                print("❌ 必须指定 --voice-id 或 --template")
                sys.exit(1)
            
            # 生成语音
            output_path = elevenlabs.text_to_speech(
                text=args.text,
                voice_id=voice_id,
                output_path=args.output,
                stability=stability,
                similarity_boost=similarity_boost,
            )
            print(f"✅ 语音已生成：{output_path}")
        
        elif args.command == "compare":
            results = compare_with_noiz(
                text=args.text,
                elevenlabs_voice_id=args.eleven_voice_id,
                noiz_ref_audio=args.noiz_audio,
                output_dir=args.output_dir,
            )
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
