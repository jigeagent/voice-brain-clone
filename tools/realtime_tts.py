#!/usr/bin/env python3
"""
实时 TTS 工具 - 低延迟语音生成

功能：
- 流式处理
- 延迟<500ms
- 实时语音变声
- RVC 集成（可选）
- So-VITS-SVC 集成（可选）

依赖：
- pyaudio
- numpy
- websocket-client (用于流式 API)
"""

import os
import json
import time
import threading
import queue
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

# ── 实时 TTS 核心 ───────────────────────────────────────────────────


class RealTimeTTS:
    """
    实时文本转语音引擎
    
    目标延迟：<500ms
    支持流式输出
    """
    
    def __init__(
        self,
        backend: str = "noiz",
        api_key: Optional[str] = None,
        sample_rate: int = 16000,
        buffer_size: int = 512,
    ):
        """
        初始化实时 TTS
        
        Args:
            backend: 后端引擎 (noiz, elevenlabs, azure, local)
            api_key: API key
            sample_rate: 采样率
            buffer_size: 音频缓冲区大小
        """
        self.backend = backend
        self.api_key = api_key
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.stats = {
            "total_chunks": 0,
            "total_latency_ms": 0,
            "avg_latency_ms": 0,
        }
    
    def text_to_speech_streaming(
        self,
        text: str,
        output_callback: Callable[[bytes], None],
        ref_audio: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        流式文本转语音
        
        Args:
            text: 要转换的文本
            output_callback: 音频数据回调函数 (接收 bytes)
            ref_audio: 参考音频（用于声音克隆）
            voice_id: 声音 ID
        
        Returns:
            性能统计 {'latency_ms': xxx, 'duration_ms': xxx}
        """
        start_time = time.perf_counter()
        
        if self.backend == "noiz":
            return self._noiz_streaming(text, output_callback, ref_audio)
        elif self.backend == "elevenlabs":
            return self._elevenlabs_streaming(text, output_callback, voice_id)
        elif self.backend == "azure":
            return self._azure_streaming(text, output_callback, voice_id)
        else:
            raise ValueError(f"不支持的后端：{self.backend}")
    
    def _noiz_streaming(
        self,
        text: str,
        output_callback: Callable[[bytes], None],
        ref_audio: Optional[str],
    ) -> Dict[str, float]:
        """Noiz API 流式调用"""
        import requests
        
        start_time = time.perf_counter()
        
        # 准备请求
        url = "https://noiz.ai/v1/text-to-speech"
        headers = {"Authorization": self.api_key}
        
        files = {}
        if ref_audio:
            files["file"] = ("ref.wav", open(ref_audio, "rb"), "audio/wav")
        
        data = {
            "text": text,
            "output_format": "pcm",  # 原始 PCM 用于流式
            "stream": "true",
        }
        
        # 发送请求
        resp = requests.post(url, headers=headers, data=data, files=files, stream=True)
        resp.raise_for_status()
        
        # 流式读取
        chunk_count = 0
        total_latency = 0
        
        for chunk in resp.iter_content(chunk_size=self.buffer_size * 2):
            chunk_start = time.perf_counter()
            
            if chunk:
                output_callback(chunk)
                chunk_count += 1
                
                chunk_latency = (time.perf_counter() - chunk_start) * 1000
                total_latency += chunk_latency
        
        end_time = time.perf_counter()
        
        return {
            "latency_ms": (end_time - start_time) * 1000,
            "duration_ms": (end_time - start_time) * 1000,
            "chunk_count": chunk_count,
            "avg_chunk_latency_ms": total_latency / chunk_count if chunk_count > 0 else 0,
        }
    
    def _elevenlabs_streaming(
        self,
        text: str,
        output_callback: Callable[[bytes], None],
        voice_id: Optional[str],
    ) -> Dict[str, float]:
        """ElevenLabs 流式调用"""
        import requests
        
        if not voice_id:
            raise ValueError("ElevenLabs 需要 voice_id")
        
        start_time = time.perf_counter()
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {"xi-api-key": self.api_key}
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
            },
        }
        
        resp = requests.post(url, json=payload, headers=headers, stream=True)
        resp.raise_for_status()
        
        chunk_count = 0
        for chunk in resp.iter_content(chunk_size=self.buffer_size * 2):
            if chunk:
                output_callback(chunk)
                chunk_count += 1
        
        end_time = time.perf_counter()
        
        return {
            "latency_ms": (end_time - start_time) * 1000,
            "duration_ms": (end_time - start_time) * 1000,
            "chunk_count": chunk_count,
        }
    
    def _azure_streaming(
        self,
        text: str,
        output_callback: Callable[[bytes], None],
        voice_id: Optional[str],
    ) -> Dict[str, float]:
        """Azure 流式调用（使用 Speech SDK）"""
        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError:
            raise ImportError("需要安装 azure-cognitiveservices-speech: pip install azure-cognitiveservices-speech")
        
        from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, ResultReason
        import tempfile
        
        start_time = time.perf_counter()
        
        # 配置
        speech_config = SpeechConfig(subscription=self.api_key, region="eastasia")
        speech_config.speech_synthesis_voice_name = voice_id or "zh-CN-XiaoxiaoNeural"
        
        # 使用 PullAudioOutputStream
        stream = speechsdk.audio.PullAudioOutputStream()
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=speechsdk.audio.AudioOutputConfig(stream=stream))
        
        # 合成
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            # 读取流式数据
            chunk_count = 0
            buffer = bytearray(self.buffer_size * 2)
            
            while True:
                read_size = stream.read(buffer)
                if read_size == 0:
                    break
                output_callback(buffer[:read_size])
                chunk_count += 1
        else:
            raise RuntimeError(f"Azure TTS 失败：{result.reason}")
        
        end_time = time.perf_counter()
        
        return {
            "latency_ms": (end_time - start_time) * 1000,
            "duration_ms": (end_time - start_time) * 1000,
            "chunk_count": chunk_count,
        }


# ── 实时变声（RVC 集成） ───────────────────────────────────────────────────


class RealTimeVoiceChanger:
    """
    实时语音变声
    
    支持：
    - RVC (Retrieval-based Voice Conversion)
    - So-VITS-SVC
    """
    
    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        sr: int = 40000,
    ):
        """
        初始化变声器
        
        Args:
            model_path: RVC 模型路径
            device: 计算设备 (cuda/cpu)
            sr: 采样率
        """
        self.model_path = Path(model_path)
        self.device = device
        self.sr = sr
        
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载 RVC 模型"""
        try:
            from rvc import RVC
            self.model = RVC(
                model_path=str(self.model_path),
                device=self.device,
                sr=self.sr,
            )
            print(f"✅ RVC 模型已加载：{self.model_path}")
        except ImportError:
            print("⚠️  RVC 未安装，变声功能不可用")
            print("安装：pip install rvc-python")
        except Exception as e:
            print(f"⚠️  RVC 模型加载失败：{e}")
    
    def convert_voice(
        self,
        audio_data: bytes,
        pitch_shift: int = 0,
        index_rate: float = 0.75,
    ) -> bytes:
        """
        转换声音
        
        Args:
            audio_data: 输入音频数据（PCM）
            pitch_shift: 音调偏移（半音）
            index_rate: 索引率
        
        Returns:
            转换后的音频数据
        """
        if self.model is None:
            return audio_data
        
        import numpy as np
        
        # 转换为 numpy 数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # 转换
        converted = self.model.infer(
            audio_array,
            pitch_shift=pitch_shift,
            index_rate=index_rate,
        )
        
        return converted.tobytes()
    
    def convert_file(
        self,
        input_path: str,
        output_path: str,
        pitch_shift: int = 0,
        index_rate: float = 0.75,
    ) -> str:
        """
        转换音频文件
        
        Args:
            input_path: 输入音频文件
            output_path: 输出音频文件
            pitch_shift: 音调偏移
            index_rate: 索引率
        
        Returns:
            输出文件路径
        """
        import librosa
        import soundfile as sf
        
        # 读取音频
        audio, sr = librosa.load(input_path, sr=self.sr)
        
        # 转换
        converted = self.model.infer(
            audio,
            pitch_shift=pitch_shift,
            index_rate=index_rate,
        )
        
        # 保存
        sf.write(output_path, converted, self.sr)
        print(f"✅ 音频转换完成：{output_path}")
        
        return output_path


# ── 延迟测试工具 ───────────────────────────────────────────────────


def test_latency(
    backend: str = "noiz",
    text: str = "测试文本",
    ref_audio: Optional[str] = None,
    voice_id: Optional[str] = None,
    iterations: int = 5,
) -> Dict[str, Any]:
    """
    测试 TTS 延迟
    
    Args:
        backend: 后端引擎
        text: 测试文本
        ref_audio: 参考音频
        voice_id: 声音 ID
        iterations: 测试次数
    
    Returns:
        延迟统计
    """
    api_key = os.environ.get("NOIZ_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    
    tts = RealTimeTTS(
        backend=backend,
        api_key=api_key,
    )
    
    latencies = []
    
    def dummy_callback(audio_data):
        pass  # 不播放，只测试延迟
    
    print(f"\n🧪 开始延迟测试 ({backend}, {iterations} 次)...")
    
    for i in range(iterations):
        try:
            stats = tts.text_to_speech_streaming(
                text=text,
                output_callback=dummy_callback,
                ref_audio=ref_audio,
                voice_id=voice_id,
            )
            latency = stats["latency_ms"]
            latencies.append(latency)
            print(f"  [{i+1}/{iterations}] 延迟：{latency:.2f} ms")
        except Exception as e:
            print(f"  [{i+1}/{iterations}] 失败：{e}")
    
    # 统计
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        result = {
            "backend": backend,
            "iterations": len(latencies),
            "avg_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(min_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "meets_target": avg_latency < 500,  # 目标 <500ms
        }
        
        print(f"\n📊 延迟统计:")
        print(f"  平均：{avg_latency:.2f} ms")
        print(f"  最小：{min_latency:.2f} ms")
        print(f"  最大：{max_latency:.2f} ms")
        print(f"  目标 (<500ms): {'✅ 达标' if result['meets_target'] else '❌ 未达标'}")
        
        return result
    else:
        return {"error": "所有测试都失败了"}


# ── 实时对话示例 ───────────────────────────────────────────────────


def interactive_demo(backend: str = "noiz", ref_audio: Optional[str] = None):
    """
    实时对话演示
    
    Args:
        backend: 后端引擎
        ref_audio: 参考音频（用于声音克隆）
    """
    import pyaudio
    
    api_key = os.environ.get("NOIZ_API_KEY")
    if not api_key:
        print("❌ 请设置 NOIZ_API_KEY 环境变量")
        return
    
    tts = RealTimeTTS(backend=backend, api_key=api_key)
    
    # 初始化音频播放
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True,
    )
    
    def play_callback(audio_data):
        stream.write(audio_data)
    
    print("\n🎙️  实时对话演示开始（输入 'quit' 退出）")
    
    while True:
        text = input("\n你说：").strip()
        if text.lower() in ["quit", "exit", "q"]:
            break
        
        if not text:
            continue
        
        print("AI: ", end="", flush=True)
        
        try:
            stats = tts.text_to_speech_streaming(
                text=text,
                output_callback=play_callback,
                ref_audio=ref_audio,
            )
            print(f"\n[延迟：{stats['latency_ms']:.2f}ms]")
        except Exception as e:
            print(f"\n❌ 错误：{e}")
    
    stream.stop_stream()
    stream.close()
    p.terminate()


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="实时 TTS 工具 - 低延迟语音生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 延迟测试
  python realtime_tts.py test-latency --backend noiz --ref-audio ref.wav
  
  # 实时对话演示
  python realtime_tts.py demo --backend noiz --ref-audio ref.wav
  
  # 变声处理
  python realtime_tts.py voice-convert input.wav -o output.wav --model rvc_model.pth
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # test-latency 命令
    test_parser = subparsers.add_parser("test-latency", help="测试延迟")
    test_parser.add_argument("--backend", default="noiz", help="后端引擎")
    test_parser.add_argument("--ref-audio", help="参考音频")
    test_parser.add_argument("--voice-id", help="声音 ID")
    test_parser.add_argument("--text", default="测试文本", help="测试文本")
    test_parser.add_argument("--iterations", type=int, default=5, help="测试次数")
    
    # demo 命令
    demo_parser = subparsers.add_parser("demo", help="实时对话演示")
    demo_parser.add_argument("--backend", default="noiz", help="后端引擎")
    demo_parser.add_argument("--ref-audio", help="参考音频")
    
    # voice-convert 命令
    convert_parser = subparsers.add_parser("voice-convert", help="声音转换")
    convert_parser.add_argument("input", help="输入音频文件")
    convert_parser.add_argument("-o", "--output", required=True, help="输出音频文件")
    convert_parser.add_argument("--model", required=True, help="RVC 模型路径")
    convert_parser.add_argument("--pitch", type=int, default=0, help="音调偏移")
    convert_parser.add_argument("--index-rate", type=float, default=0.75, help="索引率")
    
    args = parser.parse_args()
    
    try:
        if args.command == "test-latency":
            result = test_latency(
                backend=args.backend,
                text=args.text,
                ref_audio=args.ref_audio,
                voice_id=args.voice_id,
                iterations=args.iterations,
            )
            
            # 保存测试报告
            report_path = Path(f"latency_test_{args.backend}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 测试报告已保存：{report_path}")
        
        elif args.command == "demo":
            interactive_demo(
                backend=args.backend,
                ref_audio=args.ref_audio,
            )
        
        elif args.command == "voice-convert":
            changer = RealTimeVoiceChanger(model_path=args.model)
            changer.convert_file(
                input_path=args.input,
                output_path=args.output,
                pitch_shift=args.pitch,
                index_rate=args.index_rate,
            )
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
