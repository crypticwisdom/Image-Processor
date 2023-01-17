# response = [
#     {
#         "store_name": "High Fashion",
#         "shipper": "DELLYMAN",
#         "shipping_fee": "1868.50"
#     },
#     {
#         "store_name": "London Wears",
#         "shipper": "DELLYMAN",
#         "shipping_fee": "1868.50"
#     },
#     {
#         "store_name": "London Wears",
#         "shipper": "Redstar",
#         "shipping_fee": "2996.67"
#     }
# ]
#
#
# result = [
#     {
#         "store_name": "High Fashion",
#         "shipper": "DELLYMAN",
#         "shipping_fee": "1868.50"
#     },
#     {
#         "store_name": "London Wears",
#         "shipper": "DELLYMAN",
#         "shipping_fee": "1868.50"
#     },
#     {
#         "store_name": "London Wears",
#         "shipper": "Redstar",
#         "shipping_fee": "2996.67"
#     }
# ]


"""
    Notes:
        Dunder / Magic / Double UnderScore Methods;

        - methods having 2 prefix and suffix underscores "__len__()".
        - commonly used for operator overloading (Operator Overloading means giving extended meaning beyond their
                predefined operational meaning. For example operator + is used to add two integers as well as join two
                strings and merge two lists. It is achievable because '+' operator is overloaded by int class and str
                class)
        - How to overload the operators in Python ? -> Consider we have 2 or more user-defined data types (objects) and
            we have to add these objects with the binary (+) operator, it throws an error,
            because compiler don't know how to add 2 or more user-defined objects. So we have to define/override
            a dunder method called "__add__()" which is automatically invoked (called) and responsible for the action
            performed on each objects by the Binary (operator). This __add__() method should be defined on the number of
            objects available to be added by the Binary (+) operator.


        Note: All operators has a dunder method for instance:
            operator             magic method
        ________________|_________________
            +           |   __add__(self, other)
            
        - The __init__():
        - The __repr__() and __str__() are used to represent the object in string format.
        - When ever the print statement is called with an object that has a __str__() or __repr__() method, the print
        function will invoke the __str__ or __repr__ method, resulting the print() to print a string representation
        of the object.
"""


class Person:
    name = "Wisdom"

    def __init__(self):
        self.name = self.name
        ...

    def o(self):
        print(self.name)
        return self.name

    def __str__(self):
        return self.name

    def __add__(self, o):
        print(self.name + o)


person1 = Person()
person2 = Person()
print(person1 + "ds", ":", person1.o, person1)
