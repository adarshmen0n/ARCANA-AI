"""Turnkey CLI demonstration script for ARCANA AI Brain.

Allows processing any educational file (PDF, DOCX, PPTX, TXT) and prints
the extracted concepts, topological learning sequence, and generated Game Specification.
"""

import argparse
import json
from pathlib import Path
import sys

# Ensure ai-engine root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestration.pipeline import ArcanaBrainPipeline
from providers.router import ProviderRouter


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="ARCANA AI Brain — Document Processing CLI")
    parser.add_argument("file_path", help="Path to educational file (.pdf, .docx, .pptx, .txt)")
    parser.add_argument("--subject", default="Computer Science", help="Subject domain")
    parser.add_argument("--campaign", default=None, help="Campaign title")
    parser.add_argument("--output", default=None, help="Optional path to save Game Specification JSON")

    args = parser.parse_args()
    path = Path(args.file_path)

    if not path.exists():
        print(f"Error: File '{path}' does not exist.")
        sys.exit(1)

    print("=" * 70)
    print("[ARCANA AI BRAIN] DOCUMENT COMPILATION PIPELINE")
    print("=" * 70)
    print(f"Ingesting: {path.name} ({path.stat().st_size / 1024:.1f} KB)")
    print(f"Subject:   {args.subject}")
    print("-" * 70)

    file_bytes = path.read_bytes()
    pipeline = ArcanaBrainPipeline(provider_router=ProviderRouter())

    def progress(stage: str, pct: int):
        print(f"[{pct:3d}%] {stage}...")

    result = pipeline.execute_sync(
        file_bytes=file_bytes,
        filename=path.name,
        subject=args.subject,
        campaign_title=args.campaign,
        progress_callback=progress,
    )

    print("\n" + "=" * 70)
    print("✅ COMPILATION COMPLETE & VALIDATED")
    print("=" * 70)
    print(f"• Total Latency:        {result.timings_ms['total_pipeline_ms']:.2f} ms")
    print(f"• Sections Extracted:   {len(result.document.sections)}")
    print(f"• Semantic Chunks:      {len(result.chunks)}")
    print(f"• Concepts Identified:  {len(result.knowledge_graph.concepts)}")
    print(f"• Pedagogical Edges:    {len(result.learning_graph.edges)}")
    print(f"• Topological Order:    {' -> '.join(c.name for c in result.knowledge_graph.concepts)}")
    print(f"• Chapters Generated:   {len(result.game_specification.campaign.chapters)}")
    print(f"• Total Game Missions:  {result.game_specification.metadata.get('total_missions')}")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(result.game_specification.model_dump_json(indent=2), encoding="utf-8")
        print(f"\n📁 Game Specification written to: {out_path.resolve()}")
    else:
        print("\n--- SAMPLE GAME MISSION (Contract v1.0) ---")
        sample_chp = result.game_specification.campaign.chapters[0]
        if sample_chp.missions:
            m = sample_chp.missions[0]
            print(f"Mission Title:  {m.title}")
            print(f"Mechanic:       {m.mechanic.value}")
            print(f"Objective:      {m.learning_objective}")
            print(f"NPC Guide:      {m.npc.name if m.npc else 'None'}")
            print(f"XP Reward:      {m.rewards.xp} XP")
            print(f"Questions:      {len(m.questions)} questions generated")


if __name__ == "__main__":
    main()
