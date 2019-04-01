Higher
======

Task description
----------------

> Take higher
>
> recorded.mp3


Solution
--------

Given was an audio file (recorded.mp3) which contains information encoded in
the high frequencies (about 12 KHz to 20 KHz) of the frequency spectrum. To
see these information, open the file in audacity and change to the frequency
spectrum view. Note that you have to change the default settings there to
include high frequencies up to 22 KHz (default is up to 8 KHz). You will see
longer and shorter bars (see audacity.png). Longer bars encode a 1, while
shorter bars encode a 0. Reading all bars will result in the following bit
pattern:

    01101111
    01101100
    01101111
    01100001
    01000011
    01010100
    01000110
    01111011
    01001110
    00110000
    01110100
    01011111
    00111100
    01101100
    01101100
    01011111
    01100011
    00110100
    01101110
    01011111
    01100010
    00110011
    01011111
    01101000
    00110011
    00110100
    01110010
    01100100
    01111101

If you group them into items of 8 bit you get an ASCII representation of the
flag, which is: `VolgaCTF{N0t_4ll_c4n_b3_h34rd}`
