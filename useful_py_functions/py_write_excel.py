from openpyxl import Workbook
wb = Workbook()

# grab the active worksheet
ws = wb.active


# Rows can also be appended
ws.append(['name', 'result'])

ws.append(['n1', 'r1'])
ws.append(['n2', 'r2'])
ws.append(['n3', 'r3'])
ws.append(['n4', 'r4'])


# Save the file
wb.save("result.xlsx")
