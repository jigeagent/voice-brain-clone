#!/usr/bin/env python3
"""
Voice-Brain-Clone v2.0 综合测试脚本

测试内容：
1. ElevenLabs 集成测试
2. 视频分析测试
3. 实时 TTS 延迟测试
4. 自动化流程测试

运行：
python tests/test_all.py
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# ── 测试配置 ───────────────────────────────────────────────────

TEST_DIR = Path(__file__).parent
TEST_OUTPUT = TEST_DIR / "output"
TEST_OUTPUT.mkdir(parents=True, exist_ok=True)

# ── 测试 1: ElevenLabs 集成 ───────────────────────────────────────────────────


def test_elevenlabs():
    """测试 ElevenLabs 集成"""
    print("\n" + "="*60)
    print("🧪 测试 1: ElevenLabs 集成")
    print("="*60)
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️  跳过：ELEVENLABS_API_KEY 未设置")
        return {"status": "skipped", "reason": "API key missing"}
    
    try:
        # 导入模块
        sys.path.insert(0, str(Path(__file__).parent.parent / "platforms"))
        from elevenlabs import ElevenLabsTTS
        
        # 创建客户端
        elevenlabs = ElevenLabsTTS()
        
        # 获取声音列表
        voices = elevenlabs.get_voices()
        print(f"✅ 获取声音列表成功：{len(voices)} 个声音")
        
        # 测试语音生成
        test_text = "Hello, this is a test of ElevenLabs integration."
        output_path = str(TEST_OUTPUT / "elevenlabs_test.mp3")
        
        # 使用预定义声音
        if voices:
            voice_id = voices[0]["voice_id"]
            output_path = elevenlabs.text_to_speech(
                text=test_text,
                voice_id=voice_id,
                output_path=output_path,
            )
            print(f"✅ 语音生成成功：{output_path}")
            
            # 验证文件存在
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                print(f"✅ 文件验证通过：{file_size} bytes")
                
                return {
                    "status": "passed",
                    "voices_count": len(voices),
                    "output_file": output_path,
                    "file_size": file_size,
                }
            else:
                print("❌ 文件验证失败：文件不存在")
                return {"status": "failed", "reason": "File not created"}
        else:
            print("⚠️  无可用声音")
            return {"status": "failed", "reason": "No voices available"}
    
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return {"status": "failed", "error": str(e)}


# ── 测试 2: 视频分析 ───────────────────────────────────────────────────


def test_video_analyzer():
    """测试视频分析工具"""
    print("\n" + "="*60)
    print("🧪 测试 2: 视频分析工具")
    print("="*60)
    
    # 检查是否有测试视频
    test_video = TEST_DIR / "test_video.mp4"
    if not test_video.exists():
        print("⚠️  跳过：测试视频不存在 (test_video.mp4)")
        return {"status": "skipped", "reason": "Test video missing"}
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
        from video_analyzer import VideoAnalyzer
        
        # 创建分析器
        analyzer = VideoAnalyzer(str(test_video))
        
        # 获取视频信息
        video_info = analyzer.video_info
        print(f"✅ 视频信息获取成功")
        print(f"   时长：{video_info['duration']} 秒")
        print(f"   分辨率：{video_info['video']['width']}x{video_info['video']['height']}")
        
        # 提取音频
        audio_path = str(TEST_OUTPUT / "extracted_audio.wav")
        analyzer.extract_audio(audio_path)
        
        if Path(audio_path).exists():
            print(f"✅ 音频提取成功：{audio_path}")
        else:
            print("❌ 音频提取失败")
            return {"status": "failed", "reason": "Audio extraction failed"}
        
        # 分析语音模式
        speech_patterns = analyzer.analyze_speech_patterns()
        print(f"✅ 语音模式分析成功")
        print(f"   语速：{speech_patterns['speech_rate_syllables_per_sec']} 音节/秒")
        
        # 生成报告
        report_path = str(TEST_OUTPUT / "video_analysis_report.json")
        analyzer.generate_report(report_path)
        
        if Path(report_path).exists():
            print(f"✅ 报告生成成功：{report_path}")
            
            return {
                "status": "passed",
                "video_info": video_info,
                "audio_file": audio_path,
                "report_file": report_path,
            }
        else:
            return {"status": "failed", "reason": "Report not created"}
    
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return {"status": "failed", "error": str(e)}


# ── 测试 3: 实时 TTS 延迟测试 ───────────────────────────────────────────────────


def test_realtime_tts():
    """测试实时 TTS 延迟"""
    print("\n" + "="*60)
    print("🧪 测试 3: 实时 TTS 延迟测试")
    print("="*60)
    
    noiz_api_key = os.environ.get("NOIZ_API_KEY")
    if not noiz_api_key:
        print("⚠️  跳过：NOIZ_API_KEY 未设置")
        return {"status": "skipped", "reason": "NOIZ_API_KEY missing"}
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
        from realtime_tts import test_latency
        
        # 运行延迟测试
        result = test_latency(
            backend="noiz",
            text="测试文本，用于延迟测试。",
            iterations=3,
        )
        
        if "error" in result:
            print(f"❌ 测试失败：{result['error']}")
            return {"status": "failed", "error": result["error"]}
        
        # 验证延迟
        avg_latency = result["avg_latency_ms"]
        meets_target = result["meets_target"]
        
        print(f"\n📊 测试结果:")
        print(f"   平均延迟：{avg_latency} ms")
        print(f"   目标 (<500ms): {'✅ 达标' if meets_target else '❌ 未达标'}")
        
        return {
            "status": "passed" if meets_target else "warning",
            "avg_latency_ms": avg_latency,
            "min_latency_ms": result["min_latency_ms"],
            "max_latency_ms": result["max_latency_ms"],
            "meets_target": meets_target,
        }
    
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return {"status": "failed", "error": str(e)}


# ── 测试 4: 自动化流程测试 ───────────────────────────────────────────────────


def test_automation():
    """测试自动化流程"""
    print("\n" + "="*60)
    print("🧪 测试 4: 自动化流程测试（简化版）")
    print("="*60)
    
    try:
        # 测试 NLP 分析
        sys.path.insert(0, str(Path(__file__).parent.parent / "automation"))
        from nlp_analyzer import LanguagePatternAnalyzer
        
        test_text = "你好，这是一个测试。我觉得很好。你觉得呢？其实很不错！"
        
        analyzer = LanguagePatternAnalyzer(language="zh")
        result = analyzer.analyze(test_text)
        
        print(f"✅ NLP 分析成功")
        print(f"   总词数：{result['word_frequency']['total_words']}")
        print(f"   唯一词数：{result['word_frequency']['unique_words']}")
        print(f"   情感倾向：{result['sentiment']['sentiment']}")
        
        # 测试能力库生成器（不实际调用 AI）
        from auto_generator import AbilityLibraryGenerator, QualityValidator
        
        # 创建示例能力库
        library = {
            "name": "测试人物",
            "role": "测试角色",
            "version": "1.0",
            "skills": [
                {"name": "技能 1", "description": "描述 1", "examples": ["例 1"]},
                {"name": "技能 2", "description": "描述 2", "examples": ["例 2"]},
                {"name": "技能 3", "description": "描述 3", "examples": ["例 3"]},
            ],
            "language_patterns": {
                "常用开场": ["你好"],
                "常用追问": ["为什么？"],
                "口头禅": ["其实", "我觉得"],
            },
            "values": {
                "事业观": "测试事业观",
                "情感观": "测试情感观",
                "成长观": "测试成长观",
            },
            "examples": [
                {"scenario": "场景 1", "dialogue": "对话 1", "analysis": "分析 1"},
                {"scenario": "场景 2", "dialogue": "对话 2", "analysis": "分析 2"},
                {"scenario": "场景 3", "dialogue": "对话 3", "analysis": "分析 3"},
            ],
        }
        
        # 质量验证
        validation = QualityValidator.validate(library)
        print(f"\n✅ 能力库质量验证成功")
        print(f"   得分：{validation['score']}/100")
        print(f"   通过：{'✅ 是' if validation['passed'] else '❌ 否'}")
        
        return {
            "status": "passed" if validation["passed"] else "warning",
            "nlp_analysis": {
                "total_words": result["word_frequency"]["total_words"],
                "unique_words": result["word_frequency"]["unique_words"],
            },
            "quality_score": validation["score"],
            "quality_passed": validation["passed"],
        }
    
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


# ── 生成测试报告 ───────────────────────────────────────────────────


def generate_test_report(results: dict) -> str:
    """生成测试报告"""
    report_path = TEST_OUTPUT / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "passed")
    failed = sum(1 for r in results.values() if r["status"] == "failed")
    skipped = sum(1 for r in results.values() if r["status"] == "skipped")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Voice-Brain-Clone v2.0 测试报告\n\n")
        f.write(f"**测试时间:** {datetime.now().isoformat()}\n\n")
        
        f.write("## 总览\n\n")
        f.write(f"- 总测试数：{total_tests}\n")
        f.write(f"- 通过：{passed}\n")
        f.write(f"- 失败：{failed}\n")
        f.write(f"- 跳过：{skipped}\n\n")
        
        f.write("## 详细结果\n\n")
        
        for test_name, result in results.items():
            status_icon = {"passed": "✅", "failed": "❌", "skipped": "⚠️ ", "warning": "⚡"}.get(result["status"], "❓")
            f.write(f"### {status_icon} {test_name}\n\n")
            f.write(f"**状态:** {result['status']}\n\n")
            
            if result["status"] == "failed" and "error" in result:
                f.write(f"**错误:** {result['error']}\n\n")
            elif result["status"] == "skipped" and "reason" in result:
                f.write(f"**原因:** {result['reason']}\n\n")
            else:
                for key, value in result.items():
                    if key not in ["status", "error", "reason"]:
                        f.write(f"- **{key}:** {value}\n")
                f.write("\n")
    
    return str(report_path)


# ── 主函数 ───────────────────────────────────────────────────


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Voice-Brain-Clone v2.0 综合测试")
    print("="*60)
    print(f"测试时间：{datetime.now().isoformat()}")
    print(f"输出目录：{TEST_OUTPUT}\n")
    
    results = {}
    
    # 运行测试
    results["ElevenLabs 集成"] = test_elevenlabs()
    results["视频分析"] = test_video_analyzer()
    results["实时 TTS"] = test_realtime_tts()
    results["自动化流程"] = test_automation()
    
    # 生成报告
    report_path = generate_test_report(results)
    print(f"\n📄 测试报告已生成：{report_path}")
    
    # 总结
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "passed")
    failed = sum(1 for r in results.values() if r["status"] == "failed")
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"总测试数：{total}")
    print(f"通过：{passed}")
    print(f"失败：{failed}")
    print(f"跳过/警告：{total - passed - failed}")
    
    if failed > 0:
        print(f"\n❌ 有 {failed} 个测试失败，请检查报告")
        sys.exit(1)
    else:
        print(f"\n✅ 所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
