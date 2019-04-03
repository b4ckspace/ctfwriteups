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

TL;DR: Given was a RSA signature oracle, which refused to sign certain values,
that allow to execute shell commands. Use homomorphism property of RSA to
blind a value, ask the oracle to sign it and the inverse of the blinding
factor. Multiply both signature to obtain the signature of the unblinded value.

The server implements a simple plaintext protocol which allows to execute
several commands (`cd`, `cat`, `sign`, `exit`, and `leave`) with optional
parameters. Each line send to the servers starts with a signature (integer)
followed by the command and parameters; all separated by spaces.

All commands, except for `sign`, `ls`, and `dir`, validate the signature
before executing the command with its parameters. While `sign` still takes a
signature, it does not validate it. Instead, it asks for a command to sign.
Rather than signing the command with all parameters, it only signs the command
without the any parameter (see the `shlex.split` at `cmd == 'sign'`). However,
all other commands validate the signature over the command including all
parameters. Additionally, `sign` refuses to sign the commands `cat` and `cd`.

The signature is implemented as standard RSA signature without padding. We
shortly introduce the basics of RSA and modular arithmetics to understand the
vulnerability of the service.

We start with basic modular arithmetic. Our following calculations will work
like the usual calculations on integers, except for a final modulus operation.
To denote the modulus n, we append “ (mod n)” to the right, meaning that all
calculations to the left are subject to modulo operations. The modulo returns
the remainder after a division, i.e., a + b (mod n) means, that you first add
a and b, divide it by n and take the remainder as final value. For example
6 + 4 (mod 7) is 3, because 6 + 4 = 10, which divided by 7 is 1 with a
remainder of 3, i.e., 10 = 1 * 7 + 3. Many integers will have inverses in
modular arithmetic, which have the property, that, if you multiply the integer
with its inverse, you get 1. The inverse of a value a is denoted a^{-1}, so
a * a^{-1} = 1 (mod n). For a concrete example: 3 * 5 = 1 (mod 7), so 5 is the
inverse of 3 and vice versa. Having covered the most important facts about
modular arithmetics, we will continue with RSA, which makes use of it.

RSA is an asymmetric cryptography procedure that allows to encrypt and sign
values. We will focus on signatures here. For RSA, you have a public key and
a private key. The private key is used to sign values, while the public key
is used the verify the signature on values. To generate those keys, RSA first
generates two distinct primes p and q. Both primes are multiplied to form the
modulus n = p * q. You chose a value for the public exponent e, which must be
relatively prime to (p-1)(q-1). In almost all cases e = 65537 is chosen,
because it is robust and improves performance. To get the private exponet d, we
have to calculate the inverse of e (mod (p-1)(q-1)), i.e., we have
e * d = 1 (mod (p-1)(q-1)). The algorithm to calculate the inverse is called
the extended euclidean algorithm. We will not cover it here, since these
details are not important. Since we know p and q, we can calculate (p-1)(q-1)
and thus d. Since p and q are not public, an adversary cannot calculate d
without unfeasible computational resources (in fact, calculating d from the
modulus and the public exponent is equivalent to factoring n, i.e., getting p
and q from n, which is believed to be a hard problem). The values n and e form
the public key for RSA, while the values n and d form the private key.

To sign a message m with RSA, the signer calculates s = m^d (mod n). To verify
the signature, anyone can check if s^e = m (mod n), because e and n are public.
If and only if this equivalence is true, s is a valid signature for m. Since d
is private, only the signer can create signatures (the truth is: the crypto
community believes that this is the case, however, there is no proof yet).

Our vulnerable service however provides an RSA signature oracle, which,
unfortunately, does not sign all values we want it to sign. Nonetheless, there
is a property of RSA that we can use to our advantage: the multiplicative
homomorphism. This property states: Sign(m\_0) * Sign(m\_1) = Sign(m\_0 * m\_1).
Mathematically, this boils down to: m\_0^d * m\_1^d = (m\_0 * m\_1)^d (mod n).

In our attack, we combine this property together with inverses in a technique
called blinding. Assume we want a signature on m = `cat flag` (as byte sequence
which is interpreted as an large integer). Our RSA signature oracle will refuse
to sign it. However, if we choose a value k and multiply m with it, i.e.,
m\_b = m * k, there is (with high probability) no `cat` inside m\_b and we can
get a signature on m\_b using the oracle. Next, we will ask the oracle to sign
k^{-1} (the inverse of k), which is also possible since it is just a random
looking value. Using the homomorphism, we get Sign(m * k) * Sign(k^{-1} =
Sign(m * k * k^{-1}) = Sign(m * 1) = Sign(m). Yay, we just have to multiply
these two signatures (mod n) to obtain the signature for m. However, there is
one caveat left.

If you remember, the RSA signature oracle only signs the command without the
parameters, but the signatures validation is on the command with all parameters.
Our blinded value and the inverse of k are no valid command, however, they still
can contain bytes that are interpreted by shlex.split, e.g., spaces, quotes,
etc. To fix this issue, we just iterate over different values for k until we
found a value for k, for which k^{-1} and m * k contain no spaces and so on.

To summarize, our attack involves the following steps:

1. Set m = `cat flag`
2. Choose a random k
3. Calculate the inverse of k: k^{-1} (mod n)
4. Set m\_b = m * k
5. If m\_b or k^{-1} contain forbidden characters (spaces, quotes, etc.) goto
   step 2.
6. Run the `sign` command with m\_b as base64 to obtain s\_0
7. Run the `sign` command with k^{-1} as base64 to obtain s\_1
8. Set s = s\_0 * s\_1 (mod n)
9. Run `cat flag` command with the signature s
10. Submit flag and gain 100 points.

You can find the python code with all these steps in exploit.py, which will
print the flag `VolgaCTF{B1ind_y0ur_tru3_int3nti0n5}`. The original server
is provided as server.py. Note that you have to generate a new RSA key pair
to use it, since the attack cannot recover the private key. If you are lazy,
try:

    n = 35712023278405967281092707335001742500880380505674767204982483064840572151157
    e = 65537
    d = 9178529992240568120034874381658747740627015878387549261101264681449421824145

To conclude, never use RSA without padding to avoid such attacks that involve
the homomorphic property of RSA. If possible, use the PSS padding scheme or
avoid RSA at all in favor of ECC signatures (e.g. Ed25519).
