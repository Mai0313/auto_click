from typing import Any

from scrapegraphai.graphs import SmartScraperGraph


def scratch(prompt: str, source: str) -> dict[str, Any]:
    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=source,
        config={
            "llm": {"api_key": "...", "model": "openai/gpt-4o-mini"},
            "verbose": True,
            "headless": True,
        },
    )

    result_dict = smart_scraper_graph.run()
    return result_dict


if __name__ == "__main__":
    from rich.console import Console

    console = Console()

    prompt = "Extract title for me"
    source = "https://123av.com/ja/dm1/v/cawd-693"
    result_dict = scratch(prompt, source)
    console.print(result_dict)
