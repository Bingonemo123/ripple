import xlsxwriter
import time

class TrendsExel:

    def __init__(self, filename=None) -> None:
        if filename is None:
            filename = 'trends'
            filename += time.strftime("%Y%m%d")
        self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        self.worksheet = self.workbook.add_worksheet()

