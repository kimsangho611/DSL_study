

str1 = "여기까지\n입니다..\nEnd of string\n\nkkkkhh"

print(str1)

char= ""
for i in range(len(str1)):
    print("str1[{}] : {}".format(i, str1[i]))
    if str1[i] == '\n':
        if str1[i + 1] == '\n':
            break
    char += str1[i]

print("char!!!")
print(char)