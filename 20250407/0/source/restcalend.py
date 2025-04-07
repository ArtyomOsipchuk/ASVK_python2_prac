from calendar import month


cal = month(2025, 9).split('\n')
print(".. table::", cal[0])
print()
print("    " + "== " * 7)
for i in cal[2:]: print('    ' + i)
print("    " + "== " * 7)
print()
