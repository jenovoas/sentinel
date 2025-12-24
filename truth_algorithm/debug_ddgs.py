from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    results = ddgs.text("Gabriel Boric", max_results=5)
    print(json.dumps(list(results), indent=2, ensure_ascii=False))
