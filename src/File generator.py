import main

def generate_singles_from_file(path = 'URLs.json'): 
    data = main.load_data(path)
    for name, url in data.items():
        main.create_single_file(file_name=name,url=url)
        
def generate_group(path = 'URLs.json'):
    data = main.load_data(path)
    urls = data.values()
    main.create_group_file(urls,file_name='Studying resources')
        
if __name__ == '__main__':
    generate_group()