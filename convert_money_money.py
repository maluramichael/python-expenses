import json
import datetime
from pprint import pprint
import os
import sys
import math
import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "template.html"
template = templateEnv.get_template(TEMPLATE_FILE)

if not os.path.exists('build'):
    os.mkdir('build')

# todo: rename categories to mapping
# todo: create dto or dataclass for transactions, results, mapping and so on

def load_mapping():
    return json.loads(open('mapping.json').read())


def load_transactions(transactions_path):
    if not transactions_path:
        raise ValueError("transactions_path is required")

    transactions = json.loads(open(transactions_path).read())
    transactions = transactions['transactions']

    for transaction in transactions:
        year = transaction['valueDate'][:4]
        month = transaction['valueDate'][5:7]

        transaction['year'] = int(year)
        transaction['month'] = int(month)
        transaction['tags'] = []

    return transactions


def match_all_keys(transaction, pattern):
    for key, value in pattern.items():
        if key not in transaction:
            return False

        if not value in transaction[key]:
            return False

    return True


def match_one_pattern(transaction, patterns):
    for pattern in patterns:
        keys_match = match_all_keys(transaction, pattern)

        if keys_match:
            return True

    return False


def create_data_structure(year_range, mapping):
    data = {}
    for year in year_range:
        data[year] = {
            'categories': {},
            'sum': [0 for i in range(1, 13)]
        }
        for category, patterns in mapping.items():
            if category == 'Skip':
                continue

            if not category in data:
                data[year]['categories'][category] = {
                    'data': {},
                    'minimum': 0,
                    'maximum': 0,
                    'average': 0
                }

                for month in range(1, 13):
                    data[year]['categories'][category]['data'][month] = 0
    return data


def add_amount(data, year, month, category, amount):
    if category == 'Skip':
        return

    data[year]['categories'][category]['data'][month] += amount
    data[year]['categories'][category]['data'][month] = round(
        data[year]['categories'][category]['data'][month],
        2
    )
    category_data = data[year]['categories'][category]['data'].values()
    minimum = math.floor(min(category_data))
    maximum = math.floor(max(category_data))
    average = math.floor(sum(category_data) / 12)

    data[year]['categories'][category]['minimum'] = minimum
    data[year]['categories'][category]['maximum'] = maximum
    data[year]['categories'][category]['average'] = average


def walk_transactions(data, year_range, transactions, mapping):
    unmatched_transactions = []

    if not data:
        raise ValueError("data is required")

    if not year_range:
        raise ValueError("year_range is required")

    if not transactions:
        raise ValueError("transactions is required")

    if not mapping:
        raise ValueError("mapping is required")

    for year in year_range:
        for month in range(1, 13):
            for transaction in [t for t in transactions if t['year'] == year and t['month'] == month]:
                was_matched = False

                for category, patterns in mapping.items():
                    category_match = match_one_pattern(transaction, patterns)

                    if category_match:
                        was_matched = True

                        # todo: maybe remove add_amount and call a callback instead
                        # todo: so that we can do more than just add the amount outside of the walk_transactions function
                        add_amount(
                            data,
                            year,
                            month,
                            category,
                            transaction['amount']
                        )
                        break

                if not was_matched:
                    unmatched_transactions.append(transaction)

    return unmatched_transactions

def calculate_sums(year_range, mapping, data):
    if not data:
        raise ValueError("data is required")

    if not year_range:
        raise ValueError("year_range is required")

    if not mapping:
        raise ValueError("mapping is required")

    if not data:
        raise ValueError("data is required")

    for year in year_range:
        for month in range(1, 13):
            sum = 0

            for category, patterns in mapping.items():
                if category == 'Skip':
                    continue

                sum += data[year]['categories'][category]['data'][month]

            data[year]['sum'][month - 1] = round(sum, 2)


def render(data, unmatched_transactions):
    if not data:
        raise ValueError("data is required")

    if not unmatched_transactions:
        raise ValueError("unmatched_transactions is required")

    print("Rendering...")

    outputText = template.render(
        data=data, unmatched_transactions=unmatched_transactions[0:5000])

    print("Writing output...")
    with open(f"output.html", 'w') as o:
        o.write(outputText)


def get_year_range(from_year=2000):
    current_year = datetime.datetime.now().year
    return range(from_year, current_year + 1)


def main():
    # todo: add help, from_year, to_year, output_file
    transactions_path = sys.argv[1]

    if not os.path.exists(transactions_path):
        print(f"File {transactions_path} does not exist.")
        exit(1)

    transactions = load_transactions(transactions_path)
    mapping = load_mapping()
    year_range = get_year_range()
    data = create_data_structure(year_range, mapping)
    unmatched_transactions = walk_transactions(data, year_range, transactions, mapping)
    calculate_sums(data, year_range, mapping, data)
    render(data, unmatched_transactions)

if __name__ == '__main__':
    main()