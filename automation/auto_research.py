#!/usr/bin/env python3
"""
自动资料搜集工具 - 网络爬虫

功能：
- 自动搜集目标人物资料（百度百科、维基百科、新闻采访）
- 视频下载（B 站、YouTube）
- 音频提取
- 社交媒体内容抓取

依赖：
- requests
- beautifulsoup4
- youtube-dl 或 yt-dlp
"""

import os
import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ── 配置 ───────────────────────────────────────────────────

OUTPUT_DIR = Path("./research_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 百度百科爬虫 ───────────────────────────────────────────────────


class BaiduBaikeScraper:
    """百度百科爬虫"""
    
    BASE_URL = "https://baike.baidu.com"
    SEARCH_URL = f"{BASE_URL}/item/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
    
    def search(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索百科条目
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            搜索结果列表
        """
        search_url = f"{self.BASE_URL}/search"
        params = {"word": keyword}
        
        resp = self.session.get(search_url, params=params)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        # 解析搜索结果
        for item in soup.select(".result-item"):
            title_elem = item.select_one(".title")
            if title_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": self.BASE_URL + title_elem.get("href", ""),
                    "summary": item.select_one(".summary").get_text(strip=True) if item.select_one(".summary") else "",
                })
        
        return results
    
    def get_page(self, keyword: str) -> Dict[str, Any]:
        """
        获取百科页面内容
        
        Args:
            keyword: 条目关键词
        
        Returns:
            页面内容字典
        """
        url = f"{self.SEARCH_URL}{keyword}"
        resp = self.session.get(url)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 提取标题
        title = soup.select_one(".lemmaTitleWapper h1")
        title = title.get_text(strip=True) if title else keyword
        
        # 提取基本信息
        info = {}
        for row in soup.select(".basicInfo-item"):
            name = row.select_one(".basicInfo-item-name")
            value = row.select_one(".basicInfo-item-value")
            if name and value:
                info[name.get_text(strip=True)] = value.get_text(strip=True)
        
        # 提取正文
        content = []
        for para in soup.select(".para"):
            text = para.get_text(strip=True)
            if text:
                content.append(text)
        
        # 提取目录
        catalog = []
        for item in soup.select(".catalog-item"):
            text = item.get_text(strip=True)
            if text:
                catalog.append(text)
        
        return {
            "title": title,
            "url": url,
            "info": info,
            "content": content,
            "catalog": catalog,
            "crawled_at": datetime.now().isoformat(),
        }
    
    def save_page(self, keyword: str, output_dir: Optional[str] = None) -> str:
        """
        保存百科页面到文件
        
        Args:
            keyword: 条目关键词
            output_dir: 输出目录
        
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = str(OUTPUT_DIR / "baike")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取页面内容
        page_data = self.get_page(keyword)
        
        # 保存为 JSON
        json_path = output_dir / f"{keyword}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        # 保存为 Markdown
        md_path = output_dir / f"{keyword}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"来源：{page_data['url']}\n\n")
            
            if page_data['info']:
                f.write("## 基本信息\n\n")
                for k, v in page_data['info'].items():
                    f.write(f"- **{k}**: {v}\n")
                f.write("\n")
            
            f.write("## 正文\n\n")
            for i, para in enumerate(page_data['content'], 1):
                f.write(f"{para}\n\n")
        
        print(f"✅ 百科页面已保存：{md_path}")
        return str(md_path)


# ── 维基百科爬虫 ───────────────────────────────────────────────────


class WikipediaScraper:
    """维基百科爬虫"""
    
    BASE_URL = "https://zh.wikipedia.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
    
    def get_page(self, keyword: str) -> Dict[str, Any]:
        """
        获取维基百科页面
        
        Args:
            keyword: 条目关键词
        
        Returns:
            页面内容字典
        """
        url = f"{self.BASE_URL}/wiki/{keyword}"
        resp = self.session.get(url)
        
        if resp.status_code == 404:
            return {"error": "页面不存在", "url": url}
        
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 提取标题
        title = soup.select_one("#firstHeading")
        title = title.get_text(strip=True) if title else keyword
        
        # 提取正文
        content = []
        for para in soup.select("#mw-content-text .mw-parser-output p"):
            text = para.get_text(strip=True)
            if text and len(text) > 20:  # 过滤短段落
                content.append(text)
        
        # 提取目录
        catalog = []
        for item in soup.select("#toc .toclevel-1"):
            text = item.get_text(strip=True)
            if text:
                catalog.append(text)
        
        return {
            "title": title,
            "url": url,
            "content": content,
            "catalog": catalog,
            "crawled_at": datetime.now().isoformat(),
        }
    
    def save_page(self, keyword: str, output_dir: Optional[str] = None) -> str:
        """保存维基百科页面"""
        if output_dir is None:
            output_dir = str(OUTPUT_DIR / "wikipedia")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        page_data = self.get_page(keyword)
        
        if "error" in page_data:
            print(f"⚠️  {page_data['error']}: {page_data['url']}")
            return ""
        
        md_path = output_dir / f"{keyword}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"来源：{page_data['url']}\n\n")
            f.write("## 正文\n\n")
            for para in page_data['content']:
                f.write(f"{para}\n\n")
        
        print(f"✅ 维基页面已保存：{md_path}")
        return str(md_path)


# ── 视频下载工具 ───────────────────────────────────────────────────


class VideoDownloader:
    """视频下载器（支持 B 站、YouTube）"""
    
    def __init__(self, output_dir: str = "./videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_bilibili(self, url: str, quality: str = "1080") -> str:
        """
        下载 B 站视频
        
        Args:
            url: B 站视频 URL
            quality: 画质 (1080, 720, 480)
        
        Returns:
            视频文件路径
        """
        # 使用 yt-dlp 下载
        cmd = [
            "yt-dlp",
            "--format", f"bestvideo[height<={quality}]+bestaudio/best",
            "--merge-output-format", "mp4",
            "--output", str(self.output_dir / "%(title)s.%(ext)s"),
            url,
        ]
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"下载失败：{result.stderr}")
        
        # 获取下载的文件
        video_files = list(self.output_dir.glob("*.mp4"))
        if video_files:
            video_path = str(video_files[-1])
            print(f"✅ B 站视频已下载：{video_path}")
            return video_path
        else:
            raise RuntimeError("未找到下载的视频文件")
    
    def download_youtube(self, url: str, quality: str = "1080") -> str:
        """
        下载 YouTube 视频
        
        Args:
            url: YouTube 视频 URL
            quality: 画质
        
        Returns:
            视频文件路径
        """
        cmd = [
            "yt-dlp",
            "--format", f"bestvideo[height<={quality}]+bestaudio/best",
            "--merge-output-format", "mp4",
            "--output", str(self.output_dir / "%(title)s.%(ext)s"),
            "--write-sub",  # 下载字幕
            "--sub-langs", "zh-Hans,zh-Hant,en",
            url,
        ]
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"下载失败：{result.stderr}")
        
        video_files = list(self.output_dir.glob("*.mp4"))
        if video_files:
            video_path = str(video_files[-1])
            print(f"✅ YouTube 视频已下载：{video_path}")
            return video_path
        else:
            raise RuntimeError("未找到下载的视频文件")
    
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径
        
        Returns:
            音频文件路径
        """
        if output_path is None:
            output_path = str(Path(video_path).with_suffix(".wav"))
        
        import subprocess
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_path,
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 音频已提取：{output_path}")
        
        return output_path


# ── 新闻采访搜集 ───────────────────────────────────────────────────


class NewsScraper:
    """新闻采访搜集"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
    
    def search_news(
        self,
        keyword: str,
        source: str = "google",
        limit: int = 20,
    ) -> List[Dict[str, str]]:
        """
        搜索新闻
        
        Args:
            keyword: 搜索关键词
            source: 搜索引擎 (google, baidu)
            limit: 结果数量限制
        
        Returns:
            新闻列表
        """
        if source == "google":
            return self._search_google_news(keyword, limit)
        elif source == "baidu":
            return self._search_baidu_news(keyword, limit)
        else:
            raise ValueError(f"不支持的搜索引擎：{source}")
    
    def _search_google_news(self, keyword: str, limit: int) -> List[Dict[str, str]]:
        """搜索 Google 新闻"""
        url = "https://www.google.com/search"
        params = {
            "q": keyword,
            "tbm": "nws",  # news
            "num": limit,
        }
        
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        for item in soup.select(".g"):
            title_elem = item.select_one("h3")
            link_elem = item.select_one("a")
            source_elem = item.select_one(".VRdlxb")
            date_elem = item.select_one(".LfVVr")
            
            if title_elem and link_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": link_elem.get("href", ""),
                    "source": source_elem.get_text(strip=True) if source_elem else "",
                    "date": date_elem.get_text(strip=True) if date_elem else "",
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def _search_baidu_news(self, keyword: str, limit: int) -> List[Dict[str, str]]:
        """搜索百度新闻"""
        url = "https://www.baidu.com/s"
        params = {
            "wd": keyword,
            "tn": "news",
        }
        
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        for item in soup.select(".result"):
            title_elem = item.select_one(".t")
            if title_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": title_elem.find_parent("a").get("href", "") if title_elem.find_parent("a") else "",
                    "source": "",
                    "date": "",
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def save_news(
        self,
        keyword: str,
        output_dir: Optional[str] = None,
        source: str = "google",
        limit: int = 20,
    ) -> str:
        """
        保存新闻搜索结果
        
        Args:
            keyword: 搜索关键词
            output_dir: 输出目录
            source: 搜索引擎
            limit: 结果数量
        
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = str(OUTPUT_DIR / "news")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        news_list = self.search_news(keyword, source, limit)
        
        # 保存为 JSON
        json_path = output_dir / f"{keyword}_news.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "keyword": keyword,
                "source": source,
                "count": len(news_list),
                "crawled_at": datetime.now().isoformat(),
                "news": news_list,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 新闻已保存：{json_path} ({len(news_list)} 条)")
        return str(json_path)


# ── 自动化研究流程 ───────────────────────────────────────────────────


def auto_research_person(
    name: str,
    output_dir: Optional[str] = None,
    include_videos: bool = True,
    include_news: bool = True,
) -> Dict[str, Any]:
    """
    自动化研究一个人物
    
    Args:
        name: 人物姓名
        output_dir: 输出目录
        include_videos: 是否包含视频
        include_news: 是否包含新闻
    
    Returns:
        研究结果汇总
    """
    if output_dir is None:
        output_dir = str(OUTPUT_DIR / f"person_{name}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "name": name,
        "researched_at": datetime.now().isoformat(),
        "sources": {},
    }
    
    print(f"\n🔍 开始研究：{name}")
    
    # 1. 百度百科
    print("\n📚 搜集百度百科...")
    try:
        baike = BaiduBaikeScraper()
        baike_path = baike.save_page(name, str(output_dir / "baike"))
        results["sources"]["baike"] = baike_path
    except Exception as e:
        print(f"⚠️  百度百科失败：{e}")
        results["sources"]["baike"] = {"error": str(e)}
    
    # 2. 维基百科
    print("\n📚 搜集维基百科...")
    try:
        wiki = WikipediaScraper()
        wiki_path = wiki.save_page(name, str(output_dir / "wikipedia"))
        results["sources"]["wikipedia"] = wiki_path
    except Exception as e:
        print(f"⚠️  维基百科失败：{e}")
        results["sources"]["wikipedia"] = {"error": str(e)}
    
    # 3. 新闻采访
    if include_news:
        print("\n📰 搜集新闻采访...")
        try:
            news = NewsScraper()
            news_path = news.save_news(name, str(output_dir / "news"), limit=20)
            results["sources"]["news"] = news_path
        except Exception as e:
            print(f"⚠️  新闻搜集失败：{e}")
            results["sources"]["news"] = {"error": str(e)}
    
    # 4. 视频资料（需要手动提供 URL）
    if include_videos:
        print("\n📹 视频下载（需要提供 URL）")
        results["sources"]["videos"] = {
            "note": "请手动提供视频 URL，使用 VideoDownloader 下载",
            "output_dir": str(output_dir / "videos"),
        }
    
    # 保存汇总报告
    summary_path = output_dir / "research_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 研究完成！汇总报告：{summary_path}")
    
    return results


# ── CLI 命令行接口 ───────────────────────────────────────────────────


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="自动资料搜集工具 - 网络爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 研究一个人物
  python auto_research.py research "陈鲁豫"
  
  # 下载 B 站视频
  python auto_research.py download-bilibili https://www.bilibili.com/video/BV1xx
  
  # 下载 YouTube 视频
  python auto_research.py download-youtube https://www.youtube.com/watch?v=xxx
  
  # 搜索新闻
  python auto_research.py search-news "陈鲁豫" --limit 20
  
  # 提取音频
  python auto_research.py extract-audio video.mp4
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # research 命令
    research_parser = subparsers.add_parser("research", help="研究一个人物")
    research_parser.add_argument("name", help="人物姓名")
    research_parser.add_argument("-o", "--output", help="输出目录")
    research_parser.add_argument("--no-videos", action="store_true", help="不下载视频")
    research_parser.add_argument("--no-news", action="store_true", help="不搜集新闻")
    
    # download-bilibili 命令
    bilibili_parser = subparsers.add_parser("download-bilibili", help="下载 B 站视频")
    bilibili_parser.add_argument("url", help="B 站视频 URL")
    bilibili_parser.add_argument("-q", "--quality", default="1080", help="画质")
    bilibili_parser.add_argument("-o", "--output-dir", default="./videos", help="输出目录")
    
    # download-youtube 命令
    youtube_parser = subparsers.add_parser("download-youtube", help="下载 YouTube 视频")
    youtube_parser.add_argument("url", help="YouTube 视频 URL")
    youtube_parser.add_argument("-q", "--quality", default="1080", help="画质")
    youtube_parser.add_argument("-o", "--output-dir", default="./videos", help="输出目录")
    
    # search-news 命令
    news_parser = subparsers.add_parser("search-news", help="搜索新闻")
    news_parser.add_argument("keyword", help="搜索关键词")
    news_parser.add_argument("--source", default="google", help="搜索引擎")
    news_parser.add_argument("--limit", type=int, default=20, help="结果数量")
    news_parser.add_argument("-o", "--output", help="输出目录")
    
    # extract-audio 命令
    extract_parser = subparsers.add_parser("extract-audio", help="提取音频")
    extract_parser.add_argument("video", help="视频文件路径")
    extract_parser.add_argument("-o", "--output", help="输出音频路径")
    
    args = parser.parse_args()
    
    try:
        if args.command == "research":
            results = auto_research_person(
                name=args.name,
                output_dir=args.output,
                include_videos=not args.no_videos,
                include_news=not args.no_news,
            )
        
        elif args.command == "download-bilibili":
            downloader = VideoDownloader(output_dir=args.output_dir)
            video_path = downloader.download_bilibili(args.url, args.quality)
            print(f"✅ 视频已下载：{video_path}")
        
        elif args.command == "download-youtube":
            downloader = VideoDownloader(output_dir=args.output_dir)
            video_path = downloader.download_youtube(args.url, args.quality)
            print(f"✅ 视频已下载：{video_path}")
        
        elif args.command == "search-news":
            scraper = NewsScraper()
            news_path = scraper.save_news(
                args.keyword,
                output_dir=args.output,
                source=args.source,
                limit=args.limit,
            )
        
        elif args.command == "extract-audio":
            downloader = VideoDownloader()
            audio_path = downloader.extract_audio(args.video, args.output)
            print(f"✅ 音频已提取：{audio_path}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
