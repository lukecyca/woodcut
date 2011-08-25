<%
import random
my_number = random.randint(0,100)
%>
Here's a nice random number: ${my_number}

% if my_number < 50:
It is smaller than 50
% else:
It is larger or equal to 50
% endif