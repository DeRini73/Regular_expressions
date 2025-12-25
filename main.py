import csv
import re
from collections import defaultdict
from pprint import pprint

test_file = "phonebook_raw.csv"

with open(test_file, encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=";")
    contacts_list = list(rows)
pprint(contacts_list)

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

    pattern = r"(\+7|8)?\s*\(?([\d\-]+)\)?[\s\-]*(\d{2,4})[\s\-]*(\d{2,3})[\s\-]*(\d{2})?\s*(\(?\s*доб\.?\s*(\d+)\)?)?"
    match = re.search(pattern, phone)

    if not match:
        digits = re.sub(r'\D', '', phone)

        ext_match = re.search(r'доб[\.\s]*(\d+)', phone, re.IGNORECASE)
        extension = ext_match.group(1) if ext_match else ""

        if not digits:
            if extension:
                return f"доб.{extension}"
            return phone

        if digits.startswith('8'):
            digits = '+7' + digits[1:]

        if not digits.startswith('7'):
            digits = '+7' + digits

        if len(digits) >= 11:
            formatted = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

        if extension:
            formatted += f" доб.{extension}"

        return formatted

    groups = match.groups()

    area_code_raw = groups[1] if groups[1] else ""
    area_code = re.sub(r'[^\d]', '', area_code_raw)

    if len(area_code) > 3:
        area_code = area_code[:3]

    parts = []
    for i in range(2, 5):
        if groups[i]:
            parts.append(groups[i])

    if len(parts) >= 3:
        formatted_phone = f"+7({area_code}){parts[0]}-{parts[1]}-{parts[2]}"

    elif len(parts) == 2:
        formatted_phone = f"+7({area_code}){parts[0]}-{parts[1]}-00"

    elif len(parts) == 1:
        formatted_phone = f"+7({area_code}){parts[0]}-00-00"

    if groups[6]:
        formatted_phone += f" доб.{groups[6]}"

    return formatted_phone


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

with open(exit_file, "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

print(f"Данные из файла '{test_file}' отсортированы и сохранены в файл '{exit_file}'")