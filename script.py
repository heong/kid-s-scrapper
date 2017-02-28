from requests import Session,get
from html.parser import HTMLParser
from urllib.parse import urlunparse,urlparse
from sys import argv,stderr

class MyHTMLParser(HTMLParser):
    def __init__(self,*args,**kwords):
        super(self.__class__,self).__init__(*args,**kwords)
        self.saw_infobox = False
        self.saw_text_website = False
        self.WILL_SKIP_ALL = False
        self.urls = list()

    def reset(self,*args,**kwords):
        super(self.__class__,self).reset(*args,**kwords)
        self.saw_infobox = False
        self.saw_text_website = False
        self.WILL_SKIP_ALL = False

    def handle_starttag(self,tag, attrs):
        if not self.WILL_SKIP_ALL:
            if tag == 'table' and any((k == 'class' and 'infobox' in v) for (k,v) in attrs):
                self.saw_infobox = True;
            elif self.saw_infobox and self.saw_text_website and tag == 'a':
                for (attr,value)  in attrs:
                    if attr == 'href':
                        link = urlunparse(urlparse(value,scheme='http'))
                        #print(link)
                        self.urls.append(link)                        
                        self.WILL_SKIP_ALL = True
                        break
    def handle_data(self,data):
        if not self.WILL_SKIP_ALL and self.saw_infobox and data == 'Website':
            self.saw_text_website = True

def main():
    fin = 'wikipedia_links.csv'
    if len(argv) == 2:
        fin = argv[1]
    parser = MyHTMLParser()
    links_to_fetch = list()
    try:
        with open(fin,'r') as f:
            links_to_fetch = [line.replace('\n','').replace('\"','') for line in f.readlines()]
    except Exception as e:
        print(e,file=stderr)
     
    urls = list()
    with Session() as s:
        for link in links_to_fetch:
            try:
                #print(f'GET {link}')
                html = s.get(link).text
                parser.feed(html)
                parser.reset()
            except Exception as e:
               print(e,file=stderr)
    urls = parser.urls
    try:        
        with open('answers.csv','w') as file: 
            file.write(f'''"wikipedia_page","website"\n''')
            for (link,url) in zip(links_to_fetch,urls):
                file.write(f'''"{link}","{url}"\n''')
    except Exception:
        print(e,file=stderr)            

if __name__ == '__main__':
    main()
