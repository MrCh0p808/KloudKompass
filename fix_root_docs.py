import os

files_to_update = ['Tests.md', 'CHANGELOG_PHASE_2_6.md']
replacements = {
    'BashCloud': 'Kloud Kompass',
    'bashcloud': 'kloudkompass',
    '—': '-'
}

count = 0
for f in files_to_update:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        new_content = content
        for old, new in replacements.items():
            new_content = new_content.replace(old, new)
            
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            count += 1

print(f'Updated {count} root .md files.')
