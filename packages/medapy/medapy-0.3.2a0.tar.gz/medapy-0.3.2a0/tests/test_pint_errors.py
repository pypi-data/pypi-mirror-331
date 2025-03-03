from pint import Unit, UnitRegistry
# from pint import set_application_registry
# import medapy.ms_pint_formatter


ureg = UnitRegistry()
# pint.set_application_registry(ureg)
# ureg.formatter.default_format = '~ms'

a = Unit('1')
b = Unit('mohm')
c = Unit('mm')
print(type(a), a, str(a))

d = a * b
e = b * c
print(d, type(d))
print(e)


t1 = ureg.Unit('m')
t2 = ureg('cm')
print(t2)
res = t1.m_from(t2, strict=False)
print(res, type(res))

f1 = ureg('T')
f2 = ureg('Oe')
contexts = ['Gaussian']
with ureg.context(*contexts):
    res = f1.to(f2).m
print(res, type(res))
# print(res.m, type(res.m))

cond = ureg('uA/uV')
print(cond.to('siemens'))