'''number.py'''

import re


class NumberUtil:
    '''NumberUtil'''

    @staticmethod
    def to_int(src: str, fallback: int | None = 0) -> int | None:
        '''문자열을 정수로 변경'''
        find = re.findall(pattern=r'\d+', string=src)
        return int(''.join(find)) if find is not None else fallback

    @staticmethod
    def find_percent(source: str, fallbackValue: int = 0) -> int:
        find = re.search(r'\d+%', source)
        return int(find.group().replace('%', '')) if find is not None else fallbackValue

    @staticmethod
    def find_area(source: str) -> float:
        search = re.search(r'\d{0,}.\d+\s{0,1}(?=㎡)', source)
        return (float(search.group().replace(',', '')), 0)[0]
