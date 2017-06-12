def stringDivider(str):
    hashlist = list(str)
    i = 0
    counter = 1
    while i < len(str):
        if str[i] == ",":
            z = i + counter
            hashlist.insert(z, '\n')
            counter += 1
        i += 1
    hashlist.insert(len(hashlist)-1, '\n')
    str = ''.join(hashlist)
    print str


