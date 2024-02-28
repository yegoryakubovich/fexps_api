from app.repositories import AccountRepository


async def start_test():
    a = await AccountRepository().search(id_=None, username='cik', page=1)
    print(a)
    for i in a[0]:
        print(i.username)

