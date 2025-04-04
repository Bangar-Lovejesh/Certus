def foobar(orig,change):
    orig = orig.split('/')
    change = change.split('/')

    for c in change:
        if not c or c =='.':
            continue
        elif c == '..':
            if orig:
                orig.pop()
        else:
            orig.append('/'+c)

    print("/"+"".join(orig))

foobar("/facebook/instagram",'../abc/def ')
        