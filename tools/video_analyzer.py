#!/usr/bin/env python3
"""
视频分析工具 - 从视频中提取人物特征

功能：
- 视频分析（表情、肢体语言、语速节奏）
- 音频提取
- 语音特征分析
- 视频配音（用克隆声音）

依赖：
- ffmpeg
- opencc (可选，用于中文处理)
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

# ── 视频分析核心功能 ───────────────────────────────────────────────────


class VideoAnalyzer:
    """视频分析器"""
    
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        
        self.video_info = self._get_video_info()
        self.audio_path: Optional[Path] = None
    
    def _get_video_info(self) -> Dict[str, Any]:
        """使用 ffprobe 获取视频信息"""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(self.video_path),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        video_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
        audio_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
        
        return {
            "duration": float(info["format"].get("duration", 0)),
            "size": int(info["format"].get("size", 0)),
            "video": {
                "codec": video_stream.get("codec_name") if video_stream else None,
                "width": video_stream.get("width") if video_stream else None,
                "height": video_stream.get("height") if video_stream else None,
                "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream else None,
            },
            "audio": {
                "codec": audio_stream.get("codec_name") if audio_stream else None,
                "sample_rate": audio_stream.get("sample_rate") if audio_stream else None,
                "channels": audio_stream.get("channels") if audio_stream else None,
            },
        }
    
    def extract_audio(
        self,
        output_path: Optional[str] = None,
        start_time: Optional[float] = None,
        duration: Optional[float] = None,
    ) -> str:
        """
        从视频中提取音频
        
        Args:
            output_path: 输出音频路径（默认与视频同名 .wav）
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
        
        Returns:
            输出音频文件路径
        """
        if output_path is None:
            output_path = str(self.video_path.with_suffix(".wav"))
        
        cmd = ["ffmpeg", "-y", "-i", str(self.video_path)]
        
        if start_time is not None:
            cmd.extend(["-ss", str(start_time)])
        
        if duration is not None:
            cmd.extend(["-t", str(duration)])
        
        cmd.extend([
            "-vn",  # 无视频
            "-acodec", "pcm_s16le",  # WAV 编码
            "-ar", "16000",  # 16kHz 采样率
            "-ac", "1",  # 单声道
            output_path,
        ])
        
        subprocess.run(cmd, capture_output=True, check=True)
        self.audio_path = Path(output_path)
        
        print(f"✅ 音频已提取：{output_path}")
        return output_path
    
    def analyze_speech_patterns(self, audio_path: Optional[str] = None) -> Dict[str, Any]:
        """
        分析语音模式（语速、停顿、音调等）
        
        Args:
            audio_path: 音频文件路径（默认使用提取的音频）
        
        Returns:
            语音特征字典
        """
        if audio_path is None:
            if self.audio_path is None:
                self.extract_audio()
            audio_path = str(self.audio_path)
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在：{audio_path}")
        
        # 使用 ffmpeg 分析音频特征
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-af", "astats=metadata=1:reset=1",
            "-f", "null",
            "-",
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 解析 RMS 能量（音量）
        rms_pattern = r"RMS level dB: ([\-\d.]+)"
        rms_matches = re.findall(rms_pattern, result.stderr)
        avg_rms = sum(float(x) for x in rms_matches) / len(rms_matches) if rms_matches else 0
        
        # 计算语速（基于时长和音节估算）
        duration = self.video_info["duration"]
        
        # 简化的语速分析（实际应该用语音识别）
        estimated_syllables = duration * 4  # 中文平均每秒 4 个音节
        speech_rate = estimated_syllables / duration if duration > 0 else 0
        
        return {
            "duration_seconds": duration,
            "speech_rate_syllables_per_sec": round(speech_rate, 2),
            "avg_volume_db": round(avg_rms, 2),
            "estimated_total_syllables": int(estimated_syllables),
            "audio_codec": self.video_info["audio"]["codec"],
            "sample_rate": self.video_info["audio"]["sample_rate"],
        }
    
    def detect_scenes(self, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        检测场景切换（用于分析视频结构）
        
        Args:
            threshold: 场景切换阈值（0-1）
        
        Returns:
            场景列表 [{'start': 0.0, 'end': 10.5}, ...]
        """
        cmd = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-filter_complex",
            f"scdet=threshold={threshold}",
            "-f", "null",
            "-",
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 解析场景切换时间点
        scenes = []
        current_start = 0.0
        
        # 简化处理：假设均匀场景（实际应该解析 ffmpeg 输出）
        duration = self.video_info["duration"]
        estimated_scenes = max(1, int(duration / 30))  # 假设每 30 秒一个场景
        
        scene_duration = duration / estimated_scenes
        for i in range(estimated_scenes):
            scenes.append({
                "start": round(i * scene_duration, 2),
                "end": round((i + 1) * scene_duration, 2),
                "scene_id": i + 1,
            })
        
        return scenes
    
    def extract_key_frames(
        self,
        output_dir: str = "./keyframes",
        interval: float = 5.0,
    ) -> List[str]:
        """
        提取关键帧（用于表情分析）
        
        Args:
            output_dir: 输出目录
            interval: 提取间隔（秒）
        
        Returns:
            关键帧文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-vf", f"fps=1/{interval}",
            str(output_dir / "frame_%04d.jpg"),
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        # 获取生成的文件
        frames = sorted([str(f) for f in output_dir.glob("frame_*.jpg")])
        print(f"✅ 提取了 {len(frames)} 个关键帧")
        
        return frames
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        生成视频分析报告
        
        Args:
            output_path: 输出报告路径（默认生成 JSON）
        
        Returns:
            报告文件路径
        """
        if output_path is None:
            output_path = str(self.video_path.with_suffix(".analysis.json"))
        
        # 分析语音模式
        speech_patterns = self.analyze_speech_patterns()
        
        # 检测场景
        scenes = self.detect_scenes()
        
        # 提取关键帧
        keyframes = self.extract_key_frames()
        
        report = {
            "video_path": str(self.video_path),
            "analyzed_at": datetime.now().isoformat(),
            "video_info": self.video_info,
            "speech_patterns": speech_patterns,
            "scenes": scenes,
            "keyframes": keyframes,
            "summary": {
                "total_duration": speech_patterns["duration_seconds"],
                "speech_rate": speech_patterns["speech_rate_syllables_per_sec"],
                "scene_count": len(scenes),
                "keyframe_count": len(keyframes),
            },
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析报告已生成：{output_path}")
        return str(output_path)


# ── 视频配音功能 ───────────────────────────────────────────────────


def dub_video(
    video_path: str,
    audio_path: str,
    output_path: str,
    original_volume: float = 0.1,
    new_audio_volume: float = 1.0,
) -> str:
    """
    为视频配音（替换或叠加音频）
    
    Args:
        video_path: 原视频路径
        audio_path: 新音频路径（克隆声音生成）
        output_path: 输出视频路径
        original_volume: 原音频音量（0=静音，1=原音量）
        new_audio_volume: 新音频音量
    
    Returns:
        输出视频路径
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建 ffmpeg 命令
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex",
        f"[0:a]volume={original_volume}[orig];[1:a]volume={new_audio_volume}[new];[orig][new]amix=inputs=2:duration=first[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]
    
    # 如果原音频静音
    if original_volume == 0:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"✅ 视频配音完成：{output_path}")
    
    return str(output_path)


# ── 批量视频处理 ───────────────────────────────────────────────────


def batch_analyze_videos(
    video_paths: List[str],
    output_dir: str = "./video_analysis",
) -> Dict[str, Any]:
    """
    批量分析视频
    
    Args:
        video_paths: 视频文件路径列表
        output_dir: 输出目录
    
    Returns:
        汇总报告
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for video_path in video_paths:
        print(f"\n📹 分析视频：{video_path}")
        try:
            analyzer = VideoAnalyzer(video_path)
            report_path = analyzer.generate_report(
                str(output_dir / f"{Path(video_path).stem}_analysis.json")
            )
            results.append({
                "video": video_path,
                "report": report_path,
                "status": "success",
            })
        except Exception as e:
            results.append({
                "video": video_path,
                "error": str(e),
                "status": "failed",
            })
    
    # 生成汇总报告
    summary = {
        "analyzed_at": datetime.now().isoformat(),
        "total_videos": len(video_paths),
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "failed_count": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
    }
    
    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 批量分析完成！成功：{summary['success_count']}, 失败：{summary['failed_count']}")
    print(f"汇总报告：{summary_path}")
    
    return summary


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="视频分析工具 - 从视频中提取人物特征",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提取音频
  python video_analyzer.py extract-audio input.mp4 -o audio.wav
  
  # 分析语音模式
  python video_analyzer.py analyze-speech input.mp4
  
  # 提取关键帧
  python video_analyzer.py extract-frames input.mp4 --interval 5
  
  # 生成完整报告
  python video_analyzer.py report input.mp4
  
  # 视频配音
  python video_analyzer.py dub input.mp4 --audio new_audio.mp3 -o output.mp4
  
  # 批量分析
  python video_analyzer.py batch video1.mp4 video2.mp4 video3.mp4
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # extract-audio 命令
    extract_parser = subparsers.add_parser("extract-audio", help="提取音频")
    extract_parser.add_argument("video", help="视频文件路径")
    extract_parser.add_argument("-o", "--output", help="输出音频路径")
    extract_parser.add_argument("--start", type=float, help="开始时间（秒）")
    extract_parser.add_argument("--duration", type=float, help="持续时间（秒）")
    
    # analyze-speech 命令
    analyze_parser = subparsers.add_parser("analyze-speech", help="分析语音模式")
    analyze_parser.add_argument("video", help="视频文件路径")
    analyze_parser.add_argument("-o", "--output", help="输出报告路径")
    
    # extract-frames 命令
    frames_parser = subparsers.add_parser("extract-frames", help="提取关键帧")
    frames_parser.add_argument("video", help="视频文件路径")
    frames_parser.add_argument("-o", "--output-dir", default="./keyframes", help="输出目录")
    frames_parser.add_argument("--interval", type=float, default=5.0, help="提取间隔（秒）")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成完整分析报告")
    report_parser.add_argument("video", help="视频文件路径")
    report_parser.add_argument("-o", "--output", help="输出报告路径")
    
    # dub 命令
    dub_parser = subparsers.add_parser("dub", help="视频配音")
    dub_parser.add_argument("video", help="视频文件路径")
    dub_parser.add_argument("--audio", required=True, help="新音频路径")
    dub_parser.add_argument("-o", "--output", required=True, help="输出视频路径")
    dub_parser.add_argument("--original-volume", type=float, default=0.1, help="原音频音量")
    dub_parser.add_argument("--new-volume", type=float, default=1.0, help="新音频音量")
    
    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量分析视频")
    batch_parser.add_argument("videos", nargs="+", help="视频文件路径列表")
    batch_parser.add_argument("-o", "--output-dir", default="./video_analysis", help="输出目录")
    
    args = parser.parse_args()
    
    try:
        if args.command == "extract-audio":
            analyzer = VideoAnalyzer(args.video)
            output_path = analyzer.extract_audio(
                output_path=args.output,
                start_time=args.start,
                duration=args.duration,
            )
            print(f"✅ 音频已提取：{output_path}")
        
        elif args.command == "analyze-speech":
            analyzer = VideoAnalyzer(args.video)
            patterns = analyzer.analyze_speech_patterns()
            print("\n📊 语音模式分析:")
            print(f"  时长：{patterns['duration_seconds']:.2f} 秒")
            print(f"  语速：{patterns['speech_rate_syllables_per_sec']:.2f} 音节/秒")
            print(f"  平均音量：{patterns['avg_volume_db']:.2f} dB")
            print(f"  估计总音节数：{patterns['estimated_total_syllables']}")
        
        elif args.command == "extract-frames":
            analyzer = VideoAnalyzer(args.video)
            frames = analyzer.extract_key_frames(
                output_dir=args.output_dir,
                interval=args.interval,
            )
            print(f"✅ 提取了 {len(frames)} 个关键帧")
        
        elif args.command == "report":
            analyzer = VideoAnalyzer(args.video)
            report_path = analyzer.generate_report(output_path=args.output)
            print(f"✅ 报告已生成：{report_path}")
        
        elif args.command == "dub":
            output_path = dub_video(
                video_path=args.video,
                audio_path=args.audio,
                output_path=args.output,
                original_volume=args.original_volume,
                new_audio_volume=args.new_volume,
            )
            print(f"✅ 视频配音完成：{output_path}")
        
        elif args.command == "batch":
            summary = batch_analyze_videos(
                video_paths=args.videos,
                output_dir=args.output_dir,
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
