#!/usr/bin/env python3
"""残響のアルケミラ シナリオビューワー ビルドスクリプト

MDファイルからシーンデータを抽出し、scenes.js を生成する。
使い方: python build.py
"""

import os
import re
import json
import glob
from datetime import datetime

# ===== 設定 =====
SCENE_DIR = r"O:\AI_\Claudecode\資料集め\ギャルゲ―エロゲー\残響のアルケミラ\06_本文\共通ルート"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "scenes.js")


def parse_scene_file(filepath):
    """MDファイルからシーンデータを抽出する"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    title_line = lines[0] if lines else ""

    # ヘッダー解析: # 第N章「タイトル」 [—] Scene N: シーンタイトル
    m = re.match(
        r"#\s*第(\d+)章[「（](.+?)[」）]\s*[—\-]*\s*Scene\s*(\d+)\s*[:：]\s*(.+)",
        title_line,
    )
    if not m:
        return None

    chapter_num = int(m.group(1))
    chapter_title = m.group(2).strip()
    scene_num = int(m.group(3))
    scene_title = m.group(4).strip()

    # 文字数抽出
    word_count = ""
    for line in lines[1:8]:
        wm = re.match(r"文字数\s*[:：]\s*(.+)", line)
        if wm:
            word_count = wm.group(1).strip()
            break

    # 本文抽出: ヘッダー以降 ～ ## 【シーン要約】 以前
    # ヘッダー部分の --- を探す（最初の10行以内）
    header_lines = lines[:10]
    header_hr_line = None
    for i, line in enumerate(header_lines):
        if line.strip() == "---":
            header_hr_line = i
            break

    if header_hr_line is not None:
        # 標準形式: --- 以降が本文
        body_start_offset = sum(len(l) + 1 for l in lines[: header_hr_line + 1])
        body = content[body_start_offset:]
    else:
        # --- なし: タイトル行の後、空行を挟んで本文開始
        # タイトル行 + メタデータ行をスキップ
        body_line = 1  # タイトル行の次
        while body_line < len(lines) and lines[body_line].strip() == "":
            body_line += 1
        # メタデータ行（執筆日:, 文字数: など）をスキップ
        while body_line < len(lines) and re.match(
            r"(執筆日|文字数)\s*[:：]", lines[body_line]
        ):
            body_line += 1
        while body_line < len(lines) and lines[body_line].strip() == "":
            body_line += 1
        body = "\n".join(lines[body_line:])

    # シーン要約マーカーを探す
    summary_pos = body.find("## 【シーン要約】")
    if summary_pos != -1:
        body = body[:summary_pos]

    body = body.strip()

    # 末尾の --- を除去
    body = re.sub(r"\n---\s*$", "", body).strip()

    # 段落分割
    paragraphs = []
    raw_parts = re.split(r"\n\n+", body)

    for part in raw_parts:
        part = part.strip()
        if not part:
            continue

        # 段落タイプ判定
        if part in ("◇", "　　◇", "◇\n", "　◇"):
            ptype = "break"
        elif part == "---":
            ptype = "divider"
        elif "【選択肢】" in part:
            ptype = "choice_header"
        elif part.startswith("**") and ("→" in part or "隠しフラグ" in part):
            ptype = "choice"
        elif part.startswith("（選択肢") or part.startswith("（共通テキスト"):
            ptype = "choice_label"
        else:
            ptype = "text"

        pid = f"ch{chapter_num:02d}-s{scene_num:02d}-p{len(paragraphs) + 1:03d}"
        paragraphs.append({"id": pid, "type": ptype, "text": part})

    return {
        "chapter": chapter_num,
        "chapterTitle": chapter_title,
        "scene": scene_num,
        "sceneTitle": scene_title,
        "wordCount": word_count,
        "paragraphs": paragraphs,
    }


def main():
    print("残響のアルケミラ シナリオビューワー ビルド")
    print("=" * 50)

    # シーンファイル検索
    pattern = os.path.join(SCENE_DIR, "第*章_Scene*_*.md")
    files = glob.glob(pattern)

    if not files:
        print(f"エラー: シーンファイルが見つかりません\n  検索パス: {pattern}")
        return

    # 解析
    scenes = []
    skipped = []
    for f in sorted(files):
        basename = os.path.basename(f)
        # チェック結果ファイルを除外
        if basename.startswith("チェック結果"):
            continue

        scene = parse_scene_file(f)
        if scene:
            scenes.append(scene)
            p_count = len(scene["paragraphs"])
            print(
                f"  OK: 第{scene['chapter']:2d}章 Scene {scene['scene']} "
                f"「{scene['sceneTitle']}」({p_count}段落)"
            )
        else:
            skipped.append(basename)
            print(f"  SKIP: {basename}")

    # ソート（章番号→シーン番号）
    scenes.sort(key=lambda s: (s["chapter"], s["scene"]))

    # 章情報集約
    chapters = {}
    for s in scenes:
        ch = s["chapter"]
        if ch not in chapters:
            chapters[ch] = {"number": ch, "title": s["chapterTitle"], "scenes": []}
        chapters[ch]["scenes"].append(
            {
                "scene": s["scene"],
                "title": s["sceneTitle"],
                "wordCount": s["wordCount"],
            }
        )

    chapters_list = sorted(chapters.values(), key=lambda c: c["number"])

    # scenes.js 生成
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_paragraphs = sum(len(s["paragraphs"]) for s in scenes)

    js_lines = [
        f"// 残響のアルケミラ シナリオデータ（自動生成）",
        f"// 生成日時: {now}",
        f"// シーン数: {len(scenes)} / 段落数: {total_paragraphs}",
        f"",
        f"const CHAPTERS = {json.dumps(chapters_list, ensure_ascii=False)};",
        f"",
        f"const SCENES = {json.dumps(scenes, ensure_ascii=False)};",
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(js_lines))

    # ファイルサイズ
    file_size = os.path.getsize(OUTPUT_FILE)
    size_str = (
        f"{file_size / 1024:.0f}KB"
        if file_size < 1024 * 1024
        else f"{file_size / 1024 / 1024:.1f}MB"
    )

    print(f"\n{'=' * 50}")
    print(f"完了: {OUTPUT_FILE}")
    print(f"  シーン数: {len(scenes)}")
    print(f"  章数: {len(chapters)}")
    print(f"  総段落数: {total_paragraphs}")
    print(f"  ファイルサイズ: {size_str}")
    if skipped:
        print(f"  スキップ: {len(skipped)}ファイル")


if __name__ == "__main__":
    main()
