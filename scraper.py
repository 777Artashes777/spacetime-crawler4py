import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
import PartA as A
from collections import Counter
from simhash import Simhash

class Data:
    totalPages = 0
    URList = set()
    longestPage = ""
    longestNumberOfWords = 0
    wordFrequency = Counter()
    hash_values = []
    subdomain = set()
    subdomain_freq = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]
    #Store unique valid links 
    for link in valid_links:
        if link not in Data.URList:
            #We could just do len(Data.URList) to get totalPages, but kept for debugging purposes
            Data.URList.add(link)
            Data.totalPages += 1

    return valid_links

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    urls = []
    STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", 
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", 
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", 
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", 
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", 
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", 
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", 
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", 
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", 
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", 
    "you're", "you've", "your", "yours", "yourself", "yourselves"}
    #print("url:",url)
   
    if resp.status != 200:
        if (resp.status == 204 or resp.status >=300):
            return urls

    data = resp.raw_response.content
    url_data = resp.raw_response.url

    #File larger than 1.5MB ignored (data dumps, traps)
    if(len(resp.raw_response.content) > 1500000):
        return urls

    soup = BeautifulSoup(data, 'html.parser')
    text = soup.get_text(separator = ' ', strip = True)
    tokenized = re.findall(r"[a-zA-Z0-9]+", text.lower())
    tokenCount = len(tokenized)

    #Empty page or large page
    if(tokenCount == 0 or tokenCount > 100000):
        return urls
    
    cleaned_text = [token for token in tokenized if token not in STOP_WORDS]
    clean_length = len(cleaned_text)

    if((clean_length < 5) or ((clean_length/tokenCount) < 0.2)):
        return urls

    #Simhash (comparing distance between objects)
    hash_object = Simhash(cleaned_text)
    for hashed in Data.hash_values:
        if (hash_object.distance(hashed) <= 3):
            return urls
    Data.hash_values.append(hash_object)

    #If more than 50% of the text consists of the most common word, ignore
    tokenFrequency = Counter(cleaned_text)
    top_word, top_count = tokenFrequency.most_common(1)[0]
    frequency = top_count/tokenCount

    if(frequency > 0.5):
        return urls
    
    if (tokenCount > Data.longestNumberOfWords):
        Data.longestNumberOfWords = tokenCount
        Data.longestPage = url_data

    #Update frequencies
    Data.wordFrequency = Data.wordFrequency + tokenFrequency

    #Defrag absolute urls in the page
    links = soup.find_all("a")
    for link in links:
        if(link.has_attr('href')):
            href = link["href"].strip()
            if "YOUR_IP" in href or "[" in href or "]" in href:
                continue
            absolute_url = urljoin(url, href)
            defrag = (urldefrag(absolute_url))[0]
            if defrag not in urls:
                urls.append(defrag)
            
        
    parsed_url = urlparse(url_data)
    if parsed_url.hostname and re.search(r"(^|\.)ics\.uci\.edu$", parsed_url.hostname):
        defragment = (urldefrag(url_data))[0]
        
        if defragment not in Data.subdomain:
            Data.subdomain.add(defragment)
            key = parsed_url.scheme + "://" + parsed_url.hostname
            if key not in Data.subdomain_freq:
                Data.subdomain_freq[key] = 1
            else:
                Data.subdomain_freq[key] += 1
        
    #print(urls)
    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
   # matched_link 
    try:
    
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        #Gallaeries, Events on calendars
        if "/pix/" in path_lower or "/timeline" in path_lower or ("/events/" in path_lower and parsed.query):
            return False
        
        #Calendar pages
        if re.search(r"-[12]\d{3}/?$", path_lower) or re.search(r"/[12]\d{3}[01]\d{1}[0-3]\d{1}/?$", path_lower) or re.search(r"dataset$", path_lower):
            return False
        
        if re.search(r"(\?|&)(do|rev|ns|tab|view|image|media|gallery|album|share|idx|ical|outlook-ical|paged|eventDisplay)=", url.lower()):
            return False

        #Two long paths
        if len(parsed.path.split("/")) > 10:
            return False

        #Multiple versions of the same page
        if parsed.query and "version=" in parsed.query:
            return False

        if parsed.hostname is None:
            return False
        
        #Before went of all the commits (looping)
        if "gitlab.ics.uci.edu" in parsed.hostname:
            return False

        matched_link = re.search(r"(^|\.)(ics|cs|informatics|stat)\.uci\.edu$", parsed.hostname)
        today = (parsed.hostname == "today.uci.edu" and parsed.path.startswith("/department/information_computer_sciences/"))
        calendar = re.search(r"[12]\d{3}[/-]\d{2}([/-]\d{2})?", url.lower())
        #print("parsed:", parsed)


        if parsed.scheme not in set(["http", "https"]):
            return False
        if ((matched_link is None) and (not today)):
            return False
        #Main calendar pattern
        if(calendar is not None):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib|ps\.z|z)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
