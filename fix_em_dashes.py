import os

target_dir = '.coderwa'
count = 0

for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content.replace('—', '-')
                
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                count += 1

print(f'Removed em dashes from {count} files in .coderwa/')
target_dir2 = 'docs'
if os.path.exists(target_dir2):
    for root, dirs, files in os.walk(target_dir2):
        for f in files:
            if f.endswith('.md'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                new_content = content.replace('—', '-')
                    
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    count += 1
    print(f'Total updated including docs/: {count}')
