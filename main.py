import csv
import re
from collections import defaultdict


def normalize_fio(full_name):
    full_name = full_name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('"', '').strip()
    parts = full_name.split()

    if len(parts) >= 3:
        return parts[0], parts[1], " ".join(parts[2:])

    elif len(parts) == 2:
        return parts[0], parts[1], ""

    elif len(parts) == 1:
        return parts[0], "", ""

    else:
        return "", "", ""


def normalize_phone(phone):
    if not phone:
        return ""

    extension = ""
    match_extension = re.search(r'доб[авочный\.\s]*(\d+)', phone.lower())

    if match_extension:
        extension = match_extension.group(1)
        phone = re.sub(r'доб[авочный\.\s]*\d+', '', phone, flags=re.IGNORECASE).strip()

    phone = re.sub(r'[^\d]', '', phone)

    if not phone:
        if extension:
            return f"доб.{extension}"
        return ""

    if phone.startswith('8'):
        phone = '+ 7' + phone[1:]

    if phone and not phone.startswith('7'):
        phone = '+ 7' + phone

    if len(phone) == 11:
        formatted = f"+ 7({phone[1:4]}){phone[4:7]}-{phone[7:9]}-{phone[9:]}"

    elif len(phone) == 10:
        formatted = f"+ 7({phone[0:3]}){phone[3:6]}-{phone[6:8]}-{phone[8:]}"

    else:
        formatted = phone

    if extension:
        formatted = f"{formatted} доб.{extension}"

    return formatted

test_file = "data-11192014-structure-11192014.csv"

with open(test_file, encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=";")
    contacts_list = list(rows)

person_dict = defaultdict(lambda: {
    'lastname': '',
    'firstname': '',
    'surname': '',
    'organization': '',
    'position': '',
    'phone': '',
    'email': ''
})

for row in contacts_list[1:]:
    if len(row) < 13:
        continue

    org_full_name = row[1] if len(row) > 1 else ""
    head = row[3] if len(row) > 3 else ""
    deputies = row[4] if len(row) > 4 else ""
    phone = row[7] if len(row) > 7 else ""
    email = row[12] if len(row) > 12 else ""

    if head and head.strip():
        lastname, firstname, surname = normalize_fio(head)

        normalized_phone = normalize_phone(phone)

        key = f"{lastname}_{firstname}"

        if not person_dict[key]['lastname']:
            person_dict[key]['lastname'] = lastname
            person_dict[key]['firstname'] = firstname
            person_dict[key]['surname'] = surname
            person_dict[key]['organization'] = org_full_name
            person_dict[key]['position'] = 'Руководитель'
            person_dict[key]['phone'] = normalized_phone
            person_dict[key]['email'] = email.strip() if email else ""

    if deputies and deputies.strip():
        deputies_list = re.split(r'[,;\n]+', deputies)

        for deputy in deputies_list:
            deputy = deputy.strip()
            if deputy:
                lastname, firstname, surname = normalize_fio(deputy)
                normalized_phone = normalize_phone(phone)
                key = f"{lastname}_{firstname}"

                if not person_dict[key]['lastname']:
                    person_dict[key]['lastname'] = lastname
                    person_dict[key]['firstname'] = firstname
                    person_dict[key]['surname'] = surname
                    person_dict[key]['organization'] = org_full_name
                    person_dict[key]['position'] = 'Заместитель'
                    person_dict[key]['phone'] = normalized_phone
                    person_dict[key]['email'] = email.strip() if email else ""

new_contacts_list = [['lastname', 'firstname', 'surname', 'organization', 'position', 'phone', 'email']]

for person in person_dict.values():
    if person['lastname'] and person['firstname']:
        new_contacts_list.append([
            person['lastname'],
            person['firstname'],
            person['surname'],
            person['organization'],
            person['position'],
            person['phone'],
            person['email']
        ])

contacts_list = new_contacts_list

exit_file = "phonebook.csv"

with open(exit_file, "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

print(f"Данные из файла <<{test_file}>> отсортированы и сохранены в файл <<{exit_file}>>")
