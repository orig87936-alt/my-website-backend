import json

with open('../test-manus-full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"summary_zh length: {len(data['summary_zh'])}")
print(f"summary_en length: {len(data['summary_en'])}")
print(f"\nsummary_en content:")
print(data['summary_en'])

