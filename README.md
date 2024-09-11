# Getting started

Install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `exampleMapping.json` to `mapping.json` and fill in the values.

Run the following command to generate the output:

```bash
source ven/bin/activate
python3 convert_money_money.py
```

## TODO

- [ ] Add an example folder with a mapping, transactions file, screenshots and the output
- [ ] Move convert script to a `src` or `lib` folder
- [ ] Add tests
- [ ] Allow tag mapping to be empty e.g `{}` or `null`. Useful for when you want to use a tag only as a parent tag.
- [ ] Add translations for templates
- [ ] Add Support for different input formats e.g. CSV, JSON, XML and software like MoneyMoney, YNAB, etc. should be controled by command line arguments like `--input-format=MoneyMoney --transactions-file=./transactions.json`
- [ ] Add Support for generic csv format with a new mapping file or command line arguments like `--input-format=csv --date-column=1 --amount-column=5 --description-column=3`
