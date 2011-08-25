<%
    from datetime import datetime
%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <%block name="head">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Woodcut Example Site</title>
        <link rel="stylesheet" type="text/css" href="${relative_path('css/global.css')}" />
        </%block>
    </head>
    <body>
        <div id="header">
            <h1><a href="${relative_path('index.html')}">Woodcut Example Site</a></h1>
        </div>
        <div id="content">
            ${next.body()}
        </div>
        <div id="footer">
            © Woodcut ${datetime.now().year}
        </div>
    </body>
</html>
