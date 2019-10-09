import json

path = '/home/marco/vacancies.txt'

with open(path) as fd:
    json_data = json.load(fd)

    print(json.dumps(json_data, indent=4))

    print("\n\n\n")

    for item in json_data:
        print(json.dumps(item, indent=4))

        print(type(item))

        for k, v in item.items():
            print(k, v)
            print(type(v))

        print(item['vacancyExtendedInfo']['categoriaProfessionale'])

        break


