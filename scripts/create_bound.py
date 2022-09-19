id1 = 0
id2 = 1
print("\"id1\",\"id2\",\"boundary\"")
for i in range(5):
    for j in range(9):
        print(str(id1) + ", " + str(id2) + ", " + str(1))
        print(str(id2) + ", " + str(id1) + ", " + str(1))
        id1 += 1
        id2 += 1
    id1+= 1
    id2+= 1

id1 = 0
for i in range(4):
    for j in range(10):
        print(str(id1) + ", " + str(id1 + 10) + ", " + str(1))
        print(str(id1 + 10) + ", " + str(id1) + ", " + str(1))
        id1 += 1
