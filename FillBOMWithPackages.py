# https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={}
import requests
import json
import pandas as pd
import sys
from rich.progress import Progress

print("FillBOMWithPackages.py - Fill BOM with LCSC Package information")

if len(sys.argv) < 2:
    print("Usage: python Request.py <input_bom_csv> <output_bom_csv>")
    sys.exit(1)
else:
    InputBomFilePath = sys.argv[1]
    OutputBomFilePath = ""
    try:
        OutputBomFilePath = sys.argv[2]
    except IndexError:
        OutputBomFilePath = InputBomFilePath.replace(".csv", " NEW.csv")
    BomDataframe = pd.read_csv(InputBomFilePath, encoding='utf-8', dtype=str)
    NewBomDataframe = BomDataframe.copy()
    RowsLength = BomDataframe.shape[0]
    RowIdx = 0

    with Progress() as ProgressBar:
        Task = ProgressBar.add_task("[cyan]Processing BOM...", total=RowsLength)
        while not ProgressBar.finished:
            Row = BomDataframe.iloc[RowIdx]
            LcscPartNumber = Row['LCSC No.']
            if LcscPartNumber != "-":
                Response = requests.get(f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={LcscPartNumber}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'})
                Response = json.loads(Response.text)
                NewBomDataframe.iloc[RowIdx, NewBomDataframe.columns.get_loc('LCSC Package')] = Response['result']['encapStandard']
                print(f"{LcscPartNumber} -> {Response['result']['encapStandard']}")
            ProgressBar.update(Task, advance=1)
            RowIdx += 1

    NewBomDataframe.to_csv(OutputBomFilePath, index=False, encoding='utf-8-sig')
