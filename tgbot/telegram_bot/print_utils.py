

def my_print(obj, indent, logger=None):
    mydic = obj.__dict__
    for i in mydic:
        name = str(i)
        val = mydic[i]
        if val is not None:

            if name == "message" or name == "callback_query":
                if logger is None:
                    print(" " * indent + name + " : ")
                else:
                    logger.info(" " * indent + name + " : ")
                my_print(val, indent + 4, logger)
            else:
                if logger is None:
                    print(" " * indent + name + " : " + str(val))
                else:
                    logger.info(" " * indent + name + " : " + str(val))
        else:
            # print(" " * indent + name + " : None")
            pass


