from enum import Enum

class ApiInstructionContentType(Enum):
    PAGE_SOURCE = 'page_source'
    XPATH = 'xpath'
    XHR = 'xhr'