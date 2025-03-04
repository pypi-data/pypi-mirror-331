# Falla-Aol
# Sanix-darker

from twat_search.web.engines.lib_falla.core.falla import Falla


class Aol(Falla):
    def __init__(self):
        self.try_it = 0
        self.max_retry = 3
        self.source = "Aol"
        self.mode = "requests"
        self.results_box = "//div[@id='web']"
        self.each_element = {"tag": "li"}
        self.href = {"tag": "a", "type": "attribute", "key": "href", "child": {}}
        self.title = {"tag": "a", "type": "text"}
        self.cite = {"tag": "div:compText", "child": {"tag": "p", "type": "text"}}

    def search(self, search_text, pages=""):
        url = "https://search.aol.com/aol/search?q=" + search_text.replace(" ", "+") + pages

        return self.fetch(url)


# a = Aol()
# print(a.search("un avion"))
