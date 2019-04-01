Shadow Cat
==========

Task description
----------------

> We only know that one used /etc/shadow file to encrypt important message for
> us. shadow.txt encrypted.txt

Solution
--------

To be done.

TL;DR: Crack shadow file with John the Ripper, use the one-letter usernames and
their passwords to decode each letter in the ecrypted.txt.

    jr:1:17792:0:99999:7:::
    z:_:17930:0:99999:7:::
    a:a:17930:0:99999:7:::
    x:b:17930:0:99999:7:::
    q:c:17930:0:99999:7:::
    l:w:17930:0:99999:7:::
    v:h:17930:0:99999:7:::
    e:i:17930:0:99999:7:::
    f:j:17930:0:99999:7:::
    b:k:17930:0:99999:7:::
    r:l:17930:0:99999:7:::
    g:m:17930:0:99999:7:::
    n:n:17930:0:99999:7:::
    o:x:17930:0:99999:7:::
    p:y:17930:0:99999:7:::
    s:d:17930:0:99999:7:::
    c:e:17930:0:99999:7:::
    w:f:17930:0:99999:7:::
    d:g:17930:0:99999:7:::
    t:o:17930:0:99999:7:::
    h:p:17930:0:99999:7:::
    m:q:17930:0:99999:7:::
    k:u:17930:0:99999:7:::
    i:v:17930:0:99999:7:::
    y:r:17930:0:99999:7:::
    j:s:17930:0:99999:7:::
    u:t:17930:0:99999:7:::
    underscore:z:17930:0:99999:7:::

    28 password hashes cracked, 0 left

