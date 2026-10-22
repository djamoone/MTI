
print("salam alikom")
age = 124 #int

print('type of age',type(age))
salaire=3.14
print('type of age',type(salaire))
name = "djamo" 
print('type of age',type(name))

#substition
s2= "i am %s"%name
s3= "i am %d old"%age
print(s2,s3)



#list
liste = [1,2,3,4]
print('type of ls',type(liste))
print(liste)
#add element
liste.append(5)
print(liste)


#word list
worldlist = ["i","am","learning",'english']

#flow control

a=15

if a>15:
    print('a is greater than 15')
elif a<= 15 and a>=10:
    print('a between 10 and 15')
else:
    print('a is less then 10')



a=5
if a in liste:
    print("a exist in list")


#loops
for word in worldlist:
    print(word)


#loops and tests
#count occurrnece of a character in a string
chaine= 'the sky oh the sky it stretches above us vast and endless the sky is a canvas ,a canvas of blue , blue like the ocean on a clear summer day its a canvas of possiblities , possibilities as vast as the sky it self'
caracter='e'
cpt=0
for c in chaine:
    if c == caracter:
        cpt+=1

print('char %s existe %d times'%(caracter,cpt))

index = {}

print(type(index))