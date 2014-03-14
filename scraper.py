import sys,urllib,urllib2,re,os,cookielib,requests
from bs4 import BeautifulSoup

arr = []
arr2 = []
f = open('yelpEntries.txt','w')
comp = ""

def pushToFile(item):
    f.write("%s\n" %item)

def getHrefs(href):
    print "fetching %s" %href
    r = requests.get(href)
    soup = BeautifulSoup(r.text)
    #content = soup.find("#content")
    for x in soup.find_all(class_="biz-name"):
        yelpLink = str(x.get('href'))
        bizName = str(x.getText())
        if "/biz" not in yelpLink:
            print yelpLink.encode("utf-8") + "\n"
            continue
        #YELP ONLY----------------------------------------------------------------------
        formLink = getBizFromYelp("http://www.yelp.com" + yelpLink)
        if formLink == "failed":
            print "No link found \n"
            continue
        else:
            if bizName not in arr:
                arr.append(bizName)
                arr.append(formLink)
        #END YELP-----------------------------------------------------------------------
    #print r.text.encode('utf-8')
    #for line in r.text.encode('utf-8').split('\n'):
        #match = re.search(r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})', line, re.I)
        #pushToFile(line)
        #if match:
            #pushToFile(match.group(1))
    #f.close()

def getBizFromYelp(url):
    print "Going to YELP Page %s" %url
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    try:
        redirURL = str(soup.find("div", id="bizUrl").find("a").get('href'))
    except (KeyboardInterrupt, SystemExit):
            sys.exit()
    except:
        print "Error Raised, moving on\n"
        return "failed"
    redirURL = redirURL.replace("/biz_redir?url=", "")
    redirURL = redirURL.replace("http%3A%2F%2F", "http://")
    redirURL = redirURL.split("&src_bizid")[0]
    #print "\n Added: " + redirURL[0].encode("utf-8") + "\n"
    redirURL = urllib.unquote(redirURL)
    print redirURL
    return redirURL




def scrape(url):
    global comp
    links = []
    scanned = []
    skip = [".pdf","javascript:",".jpg",".png",".swf", "facebook"]

    if "\n" in url:
        url = url.replace("\n","")

    if "http:" not in url:
        print "company: %s\n" %url.encode('utf-8')
        comp = url
        return
    elif "." not in url:
        print "Not a valid URL\n"
        return
    elif "http:" in url:
        match = re.search(r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})', url, re.I)
        if match:
            pushToFile(comp.replace("\n","") + "," + match.group(1))
            print "Email Found"
            return True
        print "scanning: %s\n" %url.encode('utf-8')
        try:
            r = requests.get(url)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        except:
            print "Error Raised, moving on\n"
            return
        soup = BeautifulSoup(r.text)
        #if hasEmail(r):
            #print "email found"
            #return
        for line in r.text.encode('utf-8').split('\n'):
            #print "matching: %s" %line
            match = re.search(r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})', line, re.I)
            if match:
                pushToFile(comp.replace("\n","") + "," + match.group(1))
                print "Email Found"
                return True
        #else:
        anchors = soup.find_all('a')
        for anc in anchors:
            uri = anc.get('href')
            if uri:
                if "http" not in uri and "/" not in uri:
                    uri = url + "/" + uri
                elif "http" not in uri and uri.index("/") > 0:
                    uri = url + "/" + uri
                else:
                    uri = uri
                if "?" in uri:
                    ind = uri.index("?")
                    uri = uri[:ind]
                if r.url in uri and uri not in links and "javascript:" not in uri:
                    #print "adding: %s\n" %uri
                    links.append(uri)

        sanitizeArray(links)
        print "No email found, scanning links"
        
        for href in links:
            shouldSkip = False
            for ext in skip:
                if ext in href:
                    shouldSkip = True
                    break
            if href in scanned or shouldSkip:
                continue
            #print links
            scanned.append(href)
            if url in href:
                href = href
            elif "http" not in href:
                #need to check if on subpage and add current directory eg: http://web.com ==> http://web.com/users ==>rel url
                href = url + href
            if "?" in href:
                ind = href.index("?")
                href = href[:ind]
            print "scanning sublink %s\n" %href.encode('utf-8')
            try:
                r2 = requests.get(href)
            except (KeyboardInterrupt, SystemExit):
                sys.exit()
            except:
                print "Error Raised in sublink, moving on\n\n"
                continue
            soup2 = BeautifulSoup(r2.text)
            #if hasEmail(r):
                #print "email found"
                #return
            for line2 in r2.text.split('\n'):
                #print "matching: %s" %line2
                match = re.search(r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})', line2, re.I)
                if match:
                    pushToFile(comp.replace("\n","") + "," + match.group(1))
                    print "Email found"
                    return True
            #else:
            for subLink in soup2.find_all('a'):
                #print subLink
                subLink = subLink.get("href")
                if subLink:
                    if "../" in subLink:
                        subLink.replace("../", "")
                    if "http" not in subLink and "/" not in subLink:
                        formattedLink = url + "/" + subLink
                    else:
                        formattedLink = subLink
                    
                    if formattedLink not in links and url in formattedLink:
                        if "?" in formattedLink:
                            ind = formattedLink.index("?")
                            formattedLink = formattedLink[:ind]
                        links.append(formattedLink)
                        #print "Added: %s" %formattedLink
            sanitizeArray(links)


def hasEmail(page):
    for line in page.text.encode('utf-8').split('\n'):
        print "matching: %s" %line
        match = re.search(r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})', line, re.I)
        if match:
            pushToFile(comp)
            pushToFile(match)
            return True
        else:
            return False



def sanitizeArray(nlist):
    #remove duplicate entries
    return list(set(nlist))


fn = sys.argv[1]
file = open(fn)

for ln in file:
    #scrape(ln)
    getHrefs(ln)
arr = sanitizeArray(arr)
for prof in arr:
    #getHrefs
    pushToFile(prof)
