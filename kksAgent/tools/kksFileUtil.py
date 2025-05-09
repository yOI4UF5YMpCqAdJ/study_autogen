def kks_saveFile(save_path,content):
    with open(save_path, 'w', encoding='utf-8') as file: 
        file.write(content)
