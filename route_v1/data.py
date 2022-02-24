# %%
import random

# %%
inptfile = open("route_alloc_1.txt", 'r')
inpt = inptfile.readlines()

# %%
vn = int(inpt[0].split(sep=':')[1])
cn = int(inpt[1].split(sep=':')[1])

# %%
V = inpt[3:3+vn]
C = inpt[6+3*vn:6+3*vn+cn]

# %%
otptfile = open("inpt1.txt", 'w')
otptfile.write("4\n")
otptfile.write("48\n")
otptfile.writelines(random.sample(V, 4))
otptfile.writelines(random.sample(C, 48))


