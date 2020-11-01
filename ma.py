#from flask_marshmallow import Marshmallow
#
#
#ma = Marshmallow()
from uuid import uuid5, uuid4

id1 = int(uuid4())
id = uuid4().hex
print(id1)

print(id)


#student_d = {"Bob":96, "Ada": 89, "Chike": 86}
#
#print(student_d.items())
#print(student_d.values())
#for students in student_d:
#    print(students)
    #print(student_dict[students])



#users = [
#    ("Bob", 17, "password"),
#    ("Nancy", 16, "bob1234")
#]
#
#username_mapping = {user[0]: user for user in users}
#print(username_mapping['Bob'][2])
#
#username_input = input("Enter Your Username")
#password_input = input("Enter Your Password")
#
#username, _, password = username_mapping[username_input]
#
#if password_input == password:
#    print("Correct")
#else:
#    print("Incorrect")
#
##lis = [1,2,3,4,5,6,7]
##er = [lu for lu in lis]
##print(er)
#
#def multiply(*args):
#    total = 1
#    for arg in args:
#        total = total * arg
#    return total
#
#def apply(*argty, operator):
#    if operator == "+":
#        return sum(argty)
#    elif operator == '*':
#        return multiply(*argty)
#    else:
#        return "UNKNOWN"
#
##print(multiply(1,3,6,7))
#
#print(apply(1,3,6,7, operator="*"))