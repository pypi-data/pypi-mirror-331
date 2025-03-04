import pytokei_new

print(pytokei_new.__version__)
from rich import print

langs = pytokei_new.Languages()
langs.get_statistics(["clones/safeeq_portfolio_20250303_094428_07f32a"], ["all"], pytokei_new.Config())
language = langs.report_compact_plain()
# print(langs.get_languages_plain())

total_lines = sum(info['lines'] for info in language.values())
lang_percentage = {lang: (info['lines']/total_lines) * 100 for lang, info in language.items()}

for lang, pct in lang_percentage.items():
    print(f"{lang}: {pct:.2f}%")