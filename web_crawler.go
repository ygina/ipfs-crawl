package main

import "fmt"
import "io/ioutil"
import "net/http"
import "net/url"
import "strings"
import "sync"

import "golang.org/x/net/html"

func get_links(url_str string) []string {
	links := make([]string, 0)
	base_url, err := url.Parse(url_str)
	if err != nil {
		//fmt.Printf("Error parsing %s: %s\b", url_str, err)
		return links
	}
	resp, err := http.Get(url_str)
	if err != nil {
		//fmt.Printf("Error getting %s: %s\n", url_str, err)
		return links
	}
	contains_ipfs := false
	z := html.NewTokenizer(resp.Body)
	for {
		tt := z.Next()
		switch {
		case tt == html.ErrorToken:
			// End of document, we're done
			resp.Body.Close()
			if contains_ipfs {
				return links
			} else {
				return make([]string, 0)
			}
		case tt == html.TextToken:
			txt := string(z.Text())
			txt = strings.ToLower(txt)
			if strings.Contains(txt, "ipfs") {
				contains_ipfs = true
			}
		case tt == html.StartTagToken:
			t := z.Token()
			isAnchor := t.Data == "a"
			if !isAnchor {
				continue
			}
			for _, a := range t.Attr {
				if a.Key == "href" {
					link_url, err := url.Parse(a.Val)
					if err != nil {
						break
					}
					link_url = base_url.ResolveReference(link_url)
					links = append(links, link_url.String())
					break
				}
			}
		}
	}
}

var visited sync.Map

func is_ipfs_hash(link string) bool {
	for _, token := range([]string{
		"ipfs.io/ipfs/",
		"ipns.io/ipfs/",
		"localhost:8080/ipfs/",
		"127.0.0.1:8080/ipfs/",
	}) {
		if strings.Contains(link, token) {
			return true
		}
	}
	return false
}

func get(link string, out chan string) {
	if _, ok := visited.Load(link); ok {
		return
	} else {
		visited.Store(link, true)
	}
	new_links := get_links(link)
	for _, new_link := range(new_links) {
		if is_ipfs_hash(new_link) {
			if _, ok := visited.Load(new_link); !ok {
				visited.Store(new_link, true)
				go func(new_link string) {
					out <- new_link
				}(new_link)
			}
		} else {
			go get(new_link, out)
		}
	}
	
}

func main() {
	file, err := ioutil.ReadFile("google-search-results.txt")
	if err != nil {
		fmt.Printf("Error reading input file: %s", err)
	}
	links_to_parse := strings.Split(string(file), "\n")

	out := make(chan string)
	
	for _, link := range(links_to_parse) {
		go get(link, out)
	}

	links_found := 0
	for {
		link := <-out
		links_found++
		fmt.Printf("(%d) Found IPFS link %s\n", links_found, link)
	}
}
