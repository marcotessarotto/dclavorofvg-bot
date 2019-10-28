

def my_print(obj, indent):
    mydic = obj.__dict__
    for i in mydic:
        name = str(i)
        val = mydic[i]
        if val is not None:

            if name == "message" or name == "callback_query":
                print(" " * indent + name + " : ")
                my_print(val, indent + 4)
            else:
                print(" " * indent + name + " : " + str(val))
        else:
            # print(" " * indent + name + " : None")
            pass


