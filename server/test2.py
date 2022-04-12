a = "aaa vvv ggg".split(" ")
b = "aaa ggg".split(" ")
dif = list(set(a).difference(set(b)))
print(dif[0])

