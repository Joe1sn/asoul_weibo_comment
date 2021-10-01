with open("list.txt","r",encoding="utf-8") as comments:
    content = comments.readlines()
    print(type(content),content)
    content=list(content[0])
    print(len(content),content)
