import requests
from typing import Optional
from os.path import exists
from os import mkdir, remove
import re

html_template = """<!DOCTYPE html>
<html>
<head>
<title>Open URL</title>
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
</body>
</html>"""

def url_works(url:str) -> bool:
    """
    Checks if a URL exists and is accessible.
    Returns True if the URL returns a successful status code (2xx),
    False otherwise, including connection errors.
    """
    try:
        response = requests.head(url, timeout=5) # Add a timeout to prevent hanging
        print(f"URL successfully read, status code:{response.status_code}")
        return 200 <= response.status_code < 300
    except requests.exceptions.RequestException as e:
        # This catches various errors like ConnectionError, Timeout, TooManyRedirects, etc.
        print(f"Error checking URL {url}: {e}")
        return False

def new_file_name(directory:str, extension:str, default_name = 'New file'):
    """
    returns a filename that is not in the given directory
    """
    
    possible_file_name = default_name
    possible_file_destination = directory + '/' + possible_file_name + '.' + extension
    n = 2 #possible directory addition to avoid problems with the name 
    while exists(possible_file_destination):
        possible_file_name = default_name + f' {str(n)}'
        possible_file_destination = directory + '/' + possible_file_name + extension
        n += 1
    print(exists(possible_file_destination), possible_file_destination)
    return possible_file_name

def url_from_html_redirect(file_path, ignore_not_found = False):
    """
    Reads an HTML file with a meta refresh tag and extracts the redirect URL.

    Args:
        file_path (str): The path to the HTML file.

    Returns:
        str: The extracted URL if found, otherwise None.
    """
    if not exists(file_path):
        if not ignore_not_found:
            print(f"Error: File not found at '{file_path}'")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find the URL in the meta refresh tag
        # It looks for: <meta http-equiv="refresh" content="0; url=THE_URL_HERE">
        # It's flexible with whitespace and quotes (single or double) around 'url='
        # The (.*?) group captures the URL.
        match = re.search(r'<meta\s+http-equiv=["\']refresh["\']\s+content=["\']0;\s*url=(.*?)["\']\s*\/?>', content, re.IGNORECASE)

        if match:
            url = match.group(1).strip()
            return url
        else:
            print(f"Warning: No 'meta refresh' URL found in '{file_path}' with the expected format.")
            return None

    except Exception as e:
        print(f"An error occurred while reading or parsing '{file_path}': {e}")
        return None

def from_url_to_html_file(url:str, destination:str = 'Generated HTML files', file_name:Optional[str] = None):
    text = html_template.format(url = url)
    if url_works(url):

        if not exists(destination):
            mkdir(destination)
            print(f'New directory \"{destination}\" has been created.')
            
        if not file_name:
            file_name = new_file_name(destination, extension = 'html')

        path = destination + "/" + file_name + '.html'
        
        if not exists(path) and url_from_html_redirect(path, ignore_not_found = True) != url:
            with open(path,'w') as f:
                f.write(text)
            print(f'new file created at \"{destination}\": {file_name}.html')
            
        elif url_from_html_redirect(path) == url:
            print('The file you are trying to create already exists with its contents.')
            
        elif exists(path):
            file_name = new_file_name(destination, extension = 'html', default_name=file_name)
            path = destination + "/" + file_name + '.html'
            print(f'Warning: the name for the file was changed to {file_name}.html')
            with open(path,'w') as f:
                f.write(text)

    else:
        print(f'Failed creating the file with the next URL: {url}')
    
    print()



def test():
    from os import rmdir

    from_url_to_html_file('failing_test')
    from_url_to_html_file('https://en.wikipedia.org/wiki/Lorem_ipsum', destination='Test directory', file_name='Test')
    from_url_to_html_file('https://en.wikipedia.org/wiki/Lorem_ipsum', destination='Test directory', file_name='Test')
    from_url_to_html_file('https://www.youtube.com/watch?v=dQw4w9WgXcQ', destination='Test directory', file_name='Test')
    
    try:
        file_to_delete1 = r'Test directory\Test.html'
        file_to_delete2 = r'Test directory\Test 2.html'
        remove(file_to_delete1)
        remove(file_to_delete2)
        rmdir('Test directory')
    except FileNotFoundError as e:
        print(e)


    

if __name__ == '__main__':
    test()