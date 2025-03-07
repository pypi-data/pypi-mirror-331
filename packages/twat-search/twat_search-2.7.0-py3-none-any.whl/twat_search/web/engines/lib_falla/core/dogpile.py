# Falla-DogPile
# Sanix-darker

from twat_search.web.engines.lib_falla.core.falla import Falla


class DogPile(Falla):
    def __init__(self):
        self.try_it = 0
        self.max_retry = 3
        self.source = "DogPile"
        self.mode = "requests"
        self.results_box = "//div[@class='mainline-results']"
        self.each_element = {"tag": "div", "attr": {"class": "web-bing__result"}}
        self.href = {"tag": "a:web-bing__title", "type": "attribute", "key": "href", "child": {}}
        self.title = {"tag": "a:web-bing__title", "type": "text"}
        self.cite = {"tag": "span:web-bing__description", "type": "text"}

    def search(self, search_text, pages=""):
        url = "https://www.dogpile.com/serp?q=" + search_text.replace(" ", "+") + pages

        return self.fetch(url)


# dp = DogPile()
# print(dp.search("un avion"))
