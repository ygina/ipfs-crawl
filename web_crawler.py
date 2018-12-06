import html.parser
import sys
import urllib.parse
import urllib.request

class LinksHTMLParser(html.parser.HTMLParser):
    links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.links += [value]

def get_links(url):
    # Given a URL, load the page, and get a list of URLs
    # linked from that page.
    if url.startswith('https://boostnote.io'):
        # These always seem to error out for some reason
        print(f"Filtered boostnote.io URL: {url}")
        return []
    try:
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode(response.headers.get_content_charset())
        if 'ipfs' not in content and 'IPFS' not in content and 'Ipfs' not in content:
            print(f"Dead end found: {url}")
            return []
        parser = LinksHTMLParser()
        parser.feed(content)
        links = []
        for link in parser.links:
            full_url = urllib.parse.urljoin(site, link)
            links += [full_url]
        return links
    except Exception:
        print(f"Error accessing/parsing url {url}")
        return []
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: web_crawler.py <file>")
        exit()
    sites_to_parse = []
    sites_parsed = set()
    ipfs_hashes = set()
    f_seed = open(sys.argv[1])
    f_hashes = open('ipfs_hashes.txt', 'w')
    for site in f_seed.readlines():
        sites_to_parse += [site.strip()]

    while True:
        url = sites_to_parse[0]
        sites_to_parse = sites_to_parse[1:]
        if url in sites_parsed:
            continue
        sites_parsed.add(url)
        print(f"({len(sites_to_parse)},{len(ipfs_hashes)}) Getting links from {url}")
        links = get_links(url)
        for link in links:
            if link not in sites_parsed:
                tokens = [
                    'ipfs.io/ipfs/',
                    'ipns.io/ipfs/',
                    'localhost:8080/ipfs/',
                    '127.0.0.1:8080/ipfs/',
                ]
                if any([token in link for token in tokens]):
                    if link not in ipfs_hashes:
                        print(f"Found IPFS hash {link}")
                        ipfs_hashes.add(link)
                        f_hashes.write(link + '\n')
                else:
                    sites_to_parse += [link]
                
                

        
