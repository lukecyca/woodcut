from BeautifulSoup import BeautifulSoup, Tag

class SoupyPage(object):
    """File i/o"""
    def open(self,filename):
        fh = open(filename, 'r')
        self.soup = BeautifulSoup(fh)
        fh.close()
        
    def save(self,filename):
        fh = open(filename, 'w')
        fh.write(self.soup.prettify())
        fh.close()
    
    """Content manipulation"""
    def replace_tag(self,tag_name,tag_id,new_tag):
        self.soup.find(tag_name, { "id" : tag_id }).replaceWith(new_tag)
    
    def get_tag_attr(self,tag_name,tag_id,attr):
        return self.soup.find(tag_name, { "id" : tag_id })[attr]
        
    def set_tag_attr(self,tag_name,tag_id,attr,value):
        self.soup.find(tag_name, { "id" : tag_id })[attr] = value
    
    """Store and retrieve meta tags"""
    def get_meta_keys(self):
        return [t['name'] for t in soup.findAll('meta')]
        
    def get_meta(self,key):
        vals = self.soup.findAll('meta', { "name" : key })
        return [val['content'] for val in vals]
        
    def set_meta(self,key,value):
        meta_tag = Tag(self.soup,'meta')
        meta_tag['name'] = key
        meta_tag['content'] = value
        self.soup.head.insert(0,meta_tag)