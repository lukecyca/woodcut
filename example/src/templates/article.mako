<%inherit file="/templates/global.mako"/>

<h2>${meta.title}</h2>

<p>Posted by ${meta.author} on ${meta.date}</p>

${next.body()}

%if meta.get('next'):
<p><a href="${relative_path(meta.next.build_path)}">Next Article</a></p>
%endif
%if meta.get('previous'):
<p><a href="${relative_path(meta.previous.build_path)}">Previous Article</a></p>
%endif