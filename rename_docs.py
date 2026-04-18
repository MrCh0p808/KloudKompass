import os

target_dir = '.coderwa'
replacements = {
    'BashCloud': 'Kloud Kompass',
    'bashcloud': 'kloudkompass',
}

count = 0
for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
                
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                count += 1

print(f'Updated {count} .md files in .coderwa/')
