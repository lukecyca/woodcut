<%
import os
from mako.template import Template

DIRECTORY = 'articles'

articles = []
for filename in [x for x in os.listdir(DIRECTORY) if x.find('.mako') > 0]:
    template = Template(filename=os.path.join(DIRECTORY, filename))
    articles.append((filename, template))
    print int(u'0.5')
%>
<%inherit file="/templates/global.mako"/>
Here is a list of articles:

<ul>
% for filename, template in articles:
    <li><a href="articles/${filename.replace('.mako','')}">${template.module.title}</a> by ${template.module.author}</li>
% endfor
</ul>