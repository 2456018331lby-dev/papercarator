#!/usr/bin/env python3
"""批量处理多个论文题目。

Usage:
    python scripts/batch_run.py topics.txt --output ./batch_output

topics.txt 格式（每行一个题目）:
    多服务台排队系统性能分析与等待时间优化研究
    基于博弈论的多无人机协同任务分配研究
    基于PID控制的自动驾驶轨迹跟踪系统设计
"""

import argparse
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Batch paper generation")
    parser.add_argument("topics_file", help="Text file with one topic per line")
    parser.add_argument("--output", "-o", default="./batch_output", help="Output root directory")
    parser.add_argument("--config", "-c", help="Config YAML file")
    parser.add_argument("--no-github", action="store_true", default=True)
    parser.add_argument("--no-vscode", action="store_true", default=True)
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")
    args = parser.parse_args()

    topics_path = Path(args.topics_file)
    if not topics_path.exists():
        print(f"Error: {topics_path} not found")
        sys.exit(1)

    topics = [
        line.strip() for line in topics_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    print(f"Found {len(topics)} topics to process")
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    results = []
    for i, topic in enumerate(topics, 1):
        safe_name = topic[:30].replace(" ", "_").replace("/", "_")
        topic_dir = output_root / f"{i:03d}_{safe_name}"

        print(f"\n[{i}/{len(topics)}] {topic}")
        print(f"  Output: {topic_dir}")

        if args.dry_run:
            results.append({"topic": topic, "status": "dry_run", "dir": str(topic_dir)})
            continue

        cmd_parts = [
            sys.executable, "-m", "papercarator.cli", "run",
            f'"{topic}"',
            "--output", str(topic_dir),
            "--no-github", "--no-vscode",
        ]
        if args.config:
            cmd_parts.extend(["--config", args.config])

        cmd = " ".join(cmd_parts)
        start = time.time()

        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=False, timeout=300)
        elapsed = time.time() - start

        status = "success" if result.returncode == 0 else "failed"
        results.append({
            "topic": topic,
            "status": status,
            "elapsed": f"{elapsed:.1f}s",
            "dir": str(topic_dir),
        })

        print(f"  Status: {status} ({elapsed:.1f}s)")

    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Summary: {len(results)} topics")
    successes = sum(1 for r in results if r["status"] == "success")
    print(f"  Success: {successes}/{len(results)}")
    for r in results:
        icon = "✓" if r["status"] == "success" else "✗"
        print(f"  {icon} {r['topic'][:50]}")


if __name__ == "__main__":
    main()
