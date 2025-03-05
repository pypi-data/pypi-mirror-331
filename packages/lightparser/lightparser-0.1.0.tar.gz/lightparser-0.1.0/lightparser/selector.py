from lxml import html

class Selector:
    def __init__(self, text):
        self.tree = html.fromstring(text)

    def xpath(self, query):
        return [Selector(html.tostring(el, encoding='unicode')) for el in self.tree.xpath(query)]

    def get(self):
        result = self.tree.text_content().strip()
        return result if result else None

    def getall(self):
        return [el.strip() for el in self.tree.xpath(".//text()") if el.strip()]
