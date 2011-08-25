<%
import os
from mako.template import Template

DIRECTORY = 'articles'

articles = []
for filename in [x for x in os.listdir(DIRECTORY) if x.find('.mako') > 0]:
    template = Template(filename=os.path.join(DIRECTORY, filename),
                        input_encoding='utf-8',
                        output_encoding='utf-8',
                        )
    articles.append((filename, template))
%>
<%inherit file="/templates/global.mako"/>
Here is a list of articles:

<ul>
% for filename, template in articles:
    <li><a href="articles/${filename.replace('.mako','')}">${template.module.title}</a> by ${template.module.author}</li>
% endfor
</ul>