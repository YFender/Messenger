import re
blacklist = "' " + '"' + '" ‘ ’ “ ” ‚ „'
print("|".join(list(blacklist)))
# print(re.findall(f'"|".join(list(blacklist))', "asd]"))
print(re.findall("|".join(list(blacklist)), '"‘’“”‚ „'))
