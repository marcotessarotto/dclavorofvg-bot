
from src.ml.nss_utils import test_nss, find_most_similar_sentence

from src.backoffice.models import AiQAActivityLog


if __name__ == '__main__':

    queryset = AiQAActivityLog.objects.order_by("-id")

    udict = {}

    results_dict = {}

    for item in queryset:

        if item.user_question in udict:
            pass

        udict[item.user_question] = item

    print(udict)
    print(len(udict))

    counter = 0

    for k,v in udict.items():

        row = [v, find_most_similar_sentence(k)]

        results_dict[k] = row

        counter += 1

        if counter > 2:
            break

    print(results_dict)

    # test_nss()

    # find_most_similar_sentence("blah. ciao")

    pass
