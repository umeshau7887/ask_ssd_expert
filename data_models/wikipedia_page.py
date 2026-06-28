from dataclasses import dataclass
@dataclass
class WikipediaPage:
  title: str
  url: str
  relevant_text: str = None