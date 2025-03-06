
"""
日期格式化演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo11.xlsx"
    ed = excel2db("./demo11.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        