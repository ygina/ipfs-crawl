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
    try:
        response = urllib.request.urlopen(url)
        content = response.read().decode(response.headers.get_content_charset())
        parser = LinksHTMLParser()
        parser.feed(content)
        links = []
        for link in parser.links:
            full_url = urllib.parse.urljoin(site, link)
            links += [full_url]
            """
            parsed_url = urllib.parse.urlparse(full_url)
            parsed_trunc_url = urllib.parse.ParseResult(
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                '', '', '')
            trunc_url = parsed_trunc_url.geturl()
            links += [trunc_url]
            """
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
        print(f"Getting links from {url}")
        links = get_links(url)
        for link in links:
            if link not in sites_parsed:
                sites_to_parse += [link]
                token = 'ipfs.io/ipfs/'
                if token in link:
                    hash = link[link.find(token) + len(token):]
                    if hash not in ipfs_hashes:
                        print(f"Found IPFS hash {hash}")
                        ipfs_hashes.add(hash)
                        f_hashes.write(hash + '\n')
                
                

        
