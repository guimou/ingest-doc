from typing import List

from langchain_core.documents import Document

from langchain_community.document_loaders.web_base import WebBaseLoader
from bs4 import BeautifulSoup



class RedHatDocumentationLoader(WebBaseLoader):
    """Load `Red Hat Documentation` single-html webpages."""

    def load(self) -> List[Document]:
        """Load webpages as Documents."""
        soup = self.scrape()
        title = soup.select_one("h1", {'class':'title'}).text
        soup = soup.select_one(".book")
        # Remove unwanted sections
        unwanted_classes = ["producttitle", "subtitle", "abstract", "legalnotice"]
        for unwanted_class in unwanted_classes:
            for div in soup.find_all("div", {'class':unwanted_class}): 
                div.decompose()
            for header in soup.find_all("h2", {'class':unwanted_class}):
                header.decompose()
        for hr in soup.find_all('hr'):
            hr.decompose()
        # Find and delete anchor tag with content "Legal Notice"
        for anchor in soup.find_all('a'):
            if anchor.text == "Legal Notice":
                anchor.decompose()
        # Unwrap unwanted tags
        unwrap_tags = ["a", "div", "span", "strong", "section"]
        for tag in unwrap_tags:
            for match in soup.findAll(tag):
                match.unwrap()
        # Extract text from paragraphs
        for match in soup.findAll('p'):
            match.replace_with(match.text)
        # Remove unwanted attributes
        for tag in soup():
            for attribute in ["class", "id", "style"]:
                del tag[attribute]
        # Transform unordered lists into paragraphs
        for ul in soup.find_all('ul'):
            new_content = ""
            for li in ul.find_all('li'):
                content = li.text.replace('\n', '')
                new_content += f" - {content}\n"
            ul.replace_with(new_content)
        # Transform ordered lists into paragraphs
        for ol in soup.find_all('ol'):
            new_content = ""
            for idx, li in enumerate(ol.find_all('li'), start=1):
                content = li.text.replace('\n', '')
                new_content += f" {idx}. {content}\n"
            ol.replace_with(new_content)
        # Transform description lists into paragraphs
        for dl in soup.find_all('dl'):
            new_content = ""
            for dt in dl.find_all('dt'):
                new_content = dt.text.replace('\n', '')
                temp_soup = BeautifulSoup('', 'html.parser')
                new_tag = temp_soup.new_tag("h4")
                new_tag.string = new_content
                dt.replace_with(new_tag)
            for dd in dl.find_all('dd'):
                new_content = dd.text.replace('\n', '')
                content = dd.replace_with(new_content)
        # Unwrap dl
        for dl in soup.findAll('dl'):
            dl.unwrap()
        # Finally, unwrap the body
        #soup.unwrap()

        text = str(soup)
        text = text.replace("\t", "").replace("\xa0", " ")
        print(f"title: {title}")
        metadata = {"source": self.web_path, "title": title}
        return [Document(page_content=text, metadata=metadata)]