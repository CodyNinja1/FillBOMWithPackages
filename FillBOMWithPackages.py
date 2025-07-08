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

    print("Select the column manually to use as LCSC Part Number:")
    
    for Idx, Column in enumerate(NewBomDataframe.columns):
        print(f"{Idx + 1}. {Column}")
    
    SelectedColumn = int(input("> ")) - 1
    
    if SelectedColumn < 0 or SelectedColumn >= len(NewBomDataframe.columns):
        print("Invalid column selection!")
        sys.exit(1)
    else:
        print("Which column to use for LCSC Package output? (default: 'LCSC Package')")
        
        SelectedOutputColumnName = input(f"> ")
        if SelectedOutputColumnName.strip() == "":
            SelectedOutputColumnName = "LCSC Package"
       
        if SelectedOutputColumnName not in NewBomDataframe.columns:
            NewBomDataframe[SelectedOutputColumnName] = ""

        SelectedColumnName = NewBomDataframe.columns[SelectedColumn]
        
        with Progress() as ProgressBar:
            Task = ProgressBar.add_task("[cyan]Processing BOM...", total=RowsLength)
            while not ProgressBar.finished:
                Row = BomDataframe.iloc[RowIdx]
                LcscPartNumber = Row[SelectedColumnName]
                if LcscPartNumber != "-" and LcscPartNumber != "" and pd.notna(LcscPartNumber):
                    Response = requests.get(f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={LcscPartNumber}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'})
                    Response = json.loads(Response.text)
                    NewBomDataframe.iloc[RowIdx, NewBomDataframe.columns.get_loc(SelectedOutputColumnName)] = Response['result']['encapStandard']
                    print(f"{LcscPartNumber} -> {Response['result']['encapStandard']}")
                ProgressBar.update(Task, advance=1)
                RowIdx += 1

        NewBomDataframe.to_csv(OutputBomFilePath, index=False, encoding='utf-8-sig')
