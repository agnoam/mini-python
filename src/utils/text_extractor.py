import os

from dataclasses import dataclass
from typing import Any, Final, List
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import lxml.etree as etree
from io import StringIO

from dacite import from_dict

@dataclass
class ValuesXPathResponse:
    hits: list[Any]
    tree: etree._Element

def xml_extract_namespaces(xml_content: bytes) -> dict[str, str]:
    """
        This function extracts the namespaces from the xml's parent tag and returns them as dictionary.

        args:
            - `xml_content: bytes` - the xml content (in bytes)

        returns: dictionary - { 'name-name': 'value' }
    """
    return dict([
        node for _, node in ET.iterparse(
            StringIO(xml_content.decode("utf-8") ), events=['start-ns']
        )
    ])

def get_values_by_xpath(root: bytes | etree._Element, xpath_query: str) -> ValuesXPathResponse:
    """
        This function extracts values from the XML by xpath query.

        args:
            - `xml_content: bytes | etree._Element` - the xml content (in bytes) or generated _Element
            - `xpath_query: str` - string of the xpath query

        returns: List of all values matching the query
    """
    tree: etree._Element = None
    if type(root) == bytes:
        # In case its file content
        namespaces: dict[str, str] = xml_extract_namespaces(root)
        tree = etree.fromstring(root)

    return from_dict(data_class=ValuesXPathResponse, data={
        'hits': tree.xpath(xpath_query, namespaces=namespaces), 
        'tree': tree
    })


def extract_strings_by_style(docx_path: str, styles_names: list[str]) -> dict[str, list[str]]:
    """
        Extracts strings from docx file, by style names
        args:
            - `docx_path: str` - The path of the docx file
            - `styles_names: list[str]` - List of styles names

        returns: Dictionary of all style names with it's hits   
    """
    STYLES_XML_PATH: Final[str] = 'word/styles.xml'
    DOCUMENT_XML_PATH: Final[str] = 'word/document.xml'

    with ZipFile(docx_path, 'r') as ARCHIVE:
        STYLES_CONTENT: Final[bytes] = ARCHIVE.read(STYLES_XML_PATH)
        DOCUMENT_CONTENT: Final[bytes] = ARCHIVE.read(DOCUMENT_XML_PATH)

        # { [type_name: string]: [words] }
        results: dict[str, list[str]] = {}
        DOC_XML_ROOT: Final[etree._Element] = etree.fromstring(DOCUMENT_CONTENT)

        for style_name in styles_names:
            STYLE_XPATH_QUERY: str = f".//*[contains(@w:val,'{style_name}')]/../w:link/@w:val"
            response: ValuesXPathResponse = get_values_by_xpath(STYLES_CONTENT, STYLE_XPATH_QUERY)
            style_ids: list[str] = response.hits

            for style_id in style_ids:
                IN_DOCUMENT_XPATH_QUERY: str = f".//*[@w:val='{style_id}']/../../w:t"
                value: ValuesXPathResponse = get_values_by_xpath(DOCUMENT_CONTENT, IN_DOCUMENT_XPATH_QUERY, DOC_XML_ROOT)
                
                elements: list[etree._Element] = value.hits
                if elements:
                    results[style_name] = elements
                    for element in elements:
                        print(f'found values: {element} of type style {style_id}')
                        element.text = f'[{element.text}:{style_id}]'

        etree.ElementTree(DOC_XML_ROOT).write(os.path.join(os.path.dirname(), 'document.xml'))
        return results

if __name__ == '__main__':
    extract_strings_by_style('<path-to-docx>', ['<style_name>', '<style_name2>'])