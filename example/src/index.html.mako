<%inherit file="/templates/global.mako"/>
Here is a list of articles:

<ul>
% for article in articles:
    <li><a href="${article.build_path}">${article.title}</a> by ${article.author}</li>
% endfor
</ul>