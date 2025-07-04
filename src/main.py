import requests
from typing import Optional
from os.path import exists
from os import mkdir, remove
import re
import json

single_tab_html_template = """<!DOCTYPE html>
<html>
<head>
<title>Open URL</title>
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
</body>
</html>"""

multi_tab_html_template_a = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Tab Opener</title>
</head>
<body>
    <!-- This minimal content is just to inform the user about pop-up blockers. -->
    <!-- The script below will attempt to open tabs immediately. -->
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px; color: #555;">
        <p>Attempting to open multiple tabs...</p>
        <p>If tabs are not opening, please check your browser's pop-up blocker settings and refresh the page.</p>
    </div>

    <script>
        // Define the URLs you want to open
        const urlsToOpen = {urls};
        """
        
multi_tab_html_template_b ="""

        // Loop through the URLs and attempt to open each in a new tab
        urlsToOpen.forEach(url => {
            // window.open(url, '_blank') attempts to open the URL in a new tab/window.
            // The '_blank' second argument ensures it opens in a new tab/window.
            // Browsers are very strict about pop-up blockers, so this might be blocked.
            window.open(url, '_blank');
        });

        // Optionally, you can close this current window/tab after a short delay
        // if you truly only want to be redirected. However, this also can be
        // blocked by browsers or cause a poor user experience.
        // setTimeout(() => {
        //     window.close();
        // }, 1000); // Close after 1 second
    </script>
</body>
</html>"""

def valid_url(url:str) -> bool:
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

def new_file_name(directory:str, extension:str, default_name:str = 'New file'):
    """
    Given a base string and an extension, returns a string that represents a filename that is 
    not being used in the given directory. (so it can create a new file with a
    name that resembles the base string)
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

def read_single_url(html_string:str):
    # Regex to find the URL in the meta refresh tag
    # It looks for: <meta http-equiv="refresh" content="0; url=THE_URL_HERE">
    # It's flexible with whitespace and quotes (single or double) around 'url='
    # The (.*?) group captures the URL.
    match = re.search(r'<meta\s+http-equiv=["\']refresh["\']\s+content=["\']0;\s*url=(.*?)["\']\s*\/?>', html_string, re.IGNORECASE)

    if match:
        url:str = match.group(1).strip()
        return url
    else:
        print(f"Warning: No URL found in text with the expected format.")
        return None

def load_single_url(file_path:str, ignore_not_found:bool = False):
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
        return read_single_url(content)

    except Exception as e:
        print(f"An error occurred while reading or parsing '{file_path}': {e}")
        return None
    
def read_group_urls(html_string:str):
    """
    Extracts URLs from the 'urlsToOpen' JavaScript array within an HTML string.

    Args:
        html_string (str): The complete HTML content as a string.

    Returns:
        list: A list of strings, where each string is a URL found in the
              'urlsToOpen' array. Returns an empty list if no URLs are found
              or if the script structure is not as expected.
    """
    urls = []
    script_match = re.search(r'<script>(.*?)</script>', html_string, re.DOTALL)

    if script_match:
        script_content = script_match.group(1)
        urls_array_match = re.search(r"const urlsToOpen = \[(.*?)\];", script_content, re.DOTALL)

        if urls_array_match:
            array_content = urls_array_match.group(1)
            url_matches = re.findall(r"'(.*?)'|\"(.*?)\"", array_content)

            for match_tuple in url_matches:
                # Each match_tuple will be like ('url_if_single_quoted', '')
                # or ('', 'url_if_double_quoted'). We take the non-empty one.
                url = match_tuple[0] if match_tuple[0] else match_tuple[1]
                if url: # Ensure the extracted string is not empty
                    urls.append(url)
    return set(urls)

def load_group_urls(file_path:str, ignore_not_found:bool = False):
    
    if not exists(file_path):
        if not ignore_not_found:
            print(f"Error: File not found at '{file_path}'")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
    url_list = read_group_urls(content)
    
    return url_list

def group_text(url_list:list[str]):
    """
    Creates the text to be saved to a html file from a group of URLs
    """
    accepted_urls = []
    for url in url_list:
        if valid_url(url):
            accepted_urls.append(url)
        else:
            print(f'warning, invalid url not added: {url}')
    
    text = multi_tab_html_template_a.format(urls=accepted_urls) + multi_tab_html_template_b
    return text

def get_valid_path(
        destination:str = 'Generated HTML files', 
        file_name:Optional[str] = None, 
        extension:str = 'html', 
        default_name:str = 'New file',
        url_list:Optional[str] = None,
        overwrite = False
    ):
    if not exists(destination):
            mkdir(destination)
            print(f'New directory \"{destination}\" has been created.')
            
    if exists(destination + "/" + file_name + '.' + extension) or not file_name:
        if set(load_group_urls(path, ignore_not_found = True)) == set(url_list):
            print('The file you are trying to create already exists with its contents.')
            return None
        elif overwrite:
            pass # exits the if and filename stays the same
        else:
            file_name = new_file_name(destination, extension, default_name)
    
    path = destination + "/" + file_name + '.' + extension
    return path

def create_group_file(
    url:list[str], 
    destination:str = 'Generated HTML files', 
    file_name:str = 'New file', 
    overwrite = False
):
    
    text = group_text(url)
    path = get_valid_path(
        destination, 
        file_name, 
        default_name=file_name, 
        url_list=url, 
        overwrite=overwrite
    )
    
    if path:
        with open(path,'w') as f:
            f.write(text)
        print(f'new file created at \"{destination}\": {file_name}.html')

def single_text(url:str):
    """
    Creates the text to be saved to a html file from a single URL
    """
    if valid_url(url):
        text = single_tab_html_template.format(url=url)
        return text
    else:
        print(f'warning, invalid url not added: {url}')
    
def create_single_file(url:str, destination:str = 'Generated HTML files', file_name:str = 'New file'):
    """
    Creates a new html file that opens a set of tabs.
    """
    text = single_text(url)
    path = get_valid_path(destination, file_name, default_name=file_name, url_list=url)
    
    if path:
        with open(path,'w') as f:
            f.write(text)
        print(f'new file created at \"{destination}\": {file_name}.html')

def load_data(file_path:str) -> Optional[dict]: 
    """
    loads and returns a dictionary from a JSON file if possible, else return False.
    """

    if not exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        print(f"New file created at '{file_path}'")
        return {}
    
    # we try to read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return False
    
    # we process the data into a dictionary.
    data = json.loads(content)
    if not isinstance(data, dict):
        print(f"Warning: '{file_path}' must be a dictionary, try changing the file path.")
    else:
        return data

def test():
    from os import rmdir

    create_single_file('failing_test')
    create_single_file('https://en.wikipedia.org/wiki/Lorem_ipsum', destination='Test directory', file_name='Test')
    create_single_file('https://en.wikipedia.org/wiki/Lorem_ipsum', destination='Test directory', file_name='Test')
    create_single_file('https://www.youtube.com/watch?v=dQw4w9WgXcQ', destination='Test directory', file_name='Test')
    
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