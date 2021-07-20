

class Foo:
    def func1():
        print("function 1")
    def func2(self):
        print(id(self))
        print("function 2")



f = Foo()
print(id(f))

print("\n\nprint id")
f.func2()