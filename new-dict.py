import json

def parse_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}
    blocks = content.split('###')

    for block in blocks:
        if ':' in block:
            key, value = block.split(':', 1)
            data[key.strip()] = value.strip()

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

# 使用方法：
# parse_file('input.txt', 'output.json')

def merge_json(file1, file2, output_file):
    with open(file1, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    
    with open(file2, 'r', encoding='utf-8') as f:
        data2 = json.load(f)

    # 使用dict的update方法合并两个字典，如果有重复的key，将保留第一个字典中的值
    data1.update({key: data2[key] for key in data2 if key not in data1})

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data1, f, ensure_ascii=False)

# 使用方法：
# merge_json('file1.json', 'file2.json', 'output.json')

#parse_file('000净名百科词汇.txt', 'user-dict2.json')
merge_json('user-dict1.json', 'user-dict2.json', 'user-dict.json')