<%!
    from datetime import datetime
%>
<!DOCTYPE html>
<html>
    <head>
        <%block name="head">
        <meta charset="utf-8"><html>
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
