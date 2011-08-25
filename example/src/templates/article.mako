<%inherit file="/templates/global.mako"/>

<h2>${self.attr.title}</h2>

<p>Posted by ${self.attr.author} on ${self.attr.date}</p>

${next.body()}