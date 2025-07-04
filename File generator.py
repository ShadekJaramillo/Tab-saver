from commands import load_data
import mainout

def generate_singles_from_file(path = 'URLs.json'): 
    data = load_data(path)
    for name, url in data.items():
        mainout.from_url_to_html_file(file_name=name,url=url)
        
if __name__ == '__main__':
    generate_singles_from_file()