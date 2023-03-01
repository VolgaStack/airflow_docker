from jinja2 import Template

def f(number):
    result = list()
    for i in range(1, number):
        if i % 2 == 0:
            result.append(i)
    return result

x = int(input())
t = Template(
    "{% set even = f %}{% for i in even %}{% if loop.last %}{{i}}{% else %}{{i}} {% endif %}{% endfor %}"
)

print(t.render(f = f(x)))


