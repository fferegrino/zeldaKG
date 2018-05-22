from bs4 import BeautifulSoup, Comment

def remove_tags(soup: BeautifulSoup, tags=['script', 'link'], remove_comments=True, copy=True):
    if copy:
        soup = BeautifulSoup(str(soup),"lxml")
    if remove_comments:
        for element in soup.find_all(string=lambda text:isinstance(text,Comment)):
            element.extract()
    if tags:
        t = []
        if isinstance(tags, list):
            t.extend(tags)
        elif isinstance(tags, str):
            t.append(tags)
        for tag in t:
            for to_be_removed in soup.findAll(tag):
                to_be_removed.decompose()
    return soup