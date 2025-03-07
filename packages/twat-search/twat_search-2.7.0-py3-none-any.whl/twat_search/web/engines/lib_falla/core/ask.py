# Falla-Ask
# Sanix-darker

from twat_search.web.engines.lib_falla.core.falla import Falla


class Ask(Falla):
    def __init__(self):
        self.try_it = 0
        self.max_retry = 3
        self.source = "Ask"
        self.mode = "requests"
        self.results_box = "//div[@class='l-mid-content']"
        self.each_element = {"tag": "div", "attr": {"class": "PartialSearchResults-item"}}
        self.href = {"tag": "a:PartialSearchResults-item-title-link", "type": "attribute", "key": "href", "child": {}}
        self.title = {"tag": "a:PartialSearchResults-item-title-link", "type": "text"}
        self.cite = {"tag": "p:PartialSearchResults-item-abstract", "type": "text"}

    def search(self, search_text, pages=""):
        url = "https://www.ask.com/web?q=" + search_text.replace(" ", "+") + pages

        return self.fetch(url)


# ak = Ask()
# print(ak.search("un avion"))
