Blind
=====

Task description
----------------

> Pull the flag...if you can.
>
> nc blind.q.2019.volgactf.ru 7070
> 
> server.py

Solution
--------

To be done.

Flag: `VolgaCTF{B1ind_y0ur_tru3_int3nti0n5}`

TL;DR: Given was a RSA signature oracle, which refused to sign certain values,
which allow to execute shell commands. Use homomorphism property of RSA to
blind a value, ask the oracle to sign it and the inverse of the blinding
factor. Multiply both signature to obtain the signature of the unblinded value.
