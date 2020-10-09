from hkpy.hkpyo import IFI

print(IFI("john"))
print(IFI("context#john"))
print(IFI("context#context#john"))
print(IFI("context#<context#john>#age"))
print(IFI('context1', 'john'))
print(IFI('context1', 'context2', 'john'))
print(IFI('context1', ('context2', 'john'), 'age'))