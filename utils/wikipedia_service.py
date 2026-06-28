
from data_models.wikipedia_page import WikipediaPage
import wikipedia


def search_wikipedia(query: str):
  wikipedia.set_lang("en")
  results = wikipedia.search(query)
  pages = []
  for title in results:
    try:
      page = wikipedia.page(title)
      pages.append(WikipediaPage(title=page.title,
                                 url=page.url))
    except wikipedia.exceptions.DisambiguationError as e:
      print(f"Disambiguation error for '{title}': {e}")
      # Handle disambiguation, e.g., choose the first option or skip
      # Here, we're skipping the disambiguation pages
      continue
    except wikipedia.exceptions.PageError:
      print(f"Page not found for '{title}'")
      continue
  return pages