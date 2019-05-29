#!/usr/bin/env python3
import os
import sys
import django


sys.path.insert(0, os.getcwd().replace('/scripts', ''))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()
from orm.models import Category, Choice, Inventory, Topic


# debug and watch
watch = 1
debug = 0
if debug:
    if os.getcwd() == '/media/SDHC/projects/assess/scripts':
        debugfile = open('assess.dbg', 'w')
    else:
        debugfile = open('/tmp/assess.dbg', 'w')
    debugfile.write('... init_assess.py\n')

# parse the command line
options = 0
for arg in sys.argv:
    options = options + 1
if options != 2:
    print('usage: python init_assess.py [type = '
          'interests.txt | skills.txt | values.txt]')
    sys.exit(0)

file = open(str(sys.argv[1]), 'r')
line = file.readline().rstrip()
if watch:
    print(line)

# input has strict order
if line == '[inventory]':

    # init an inventory
    line = file.readline().rstrip()
    if watch:
        print(line)
    inv = Inventory(type=line)
    if debug: 
        debugfile.write('\ntype: ')
        debugfile.write(str(line))

    # get the title
    line = file.readline().rstrip()
    if watch:
        print(line)
    if line == '[title]':
        line = file.readline().rstrip()
        if watch:
            print(line)
        inv.title = line
        if debug: 
            debugfile.write('\ntitle: ')
            debugfile.write(str(line))
    else:
        print('error: [title] tag missing')
        sys.exit(0)
    
    # get the tagline
    line = file.readline().rstrip()
    if watch:
        print(line)
    if line == '[tagline]':
        line = file.readline().rstrip()
        if watch:
            print(line)
        inv.tagline = "\"" + line + "\""
        if debug: 
            debugfile.write('\ntagline: ')
            debugfile.write(str(line))
    else:
        print('error: [tagline] tag missing')
        sys.exit(0)

    # get the description
    line = file.readline().rstrip()
    if watch:
        print(line)
    if line == '[description]':
        line = file.readline().rstrip()
        if watch:
            print(line)
        inv.description = line
        if debug: 
            debugfile.write('\ndescription: ')
            debugfile.write(str(line))
    else:
        print('error: [description] tag missing')
        sys.exit(0)

    # get the instructions
    line = file.readline().rstrip()
    if watch:
        print(line)
    if line == '[instructions]':
        line = file.readline().rstrip()
        if watch:
            print(line)
        inv.instructions = line
        if debug: 
            debugfile.write('\ninstructions: ')
            debugfile.write(str(line))
    else:
        print('error: [instructions] tag missing')
        sys.exit(0)

    # get the choices
    inv.save()
    line = file.readline().rstrip()
    if watch:
        print(line)
    if line == '[choices]':

        # get yellow choices
        line = file.readline().rstrip()
        if watch:
            print(line)
        options = line.split(';')
        for option in options:
            if watch:
                print(option)
            if debug: 
                debugfile.write('\noption: ')
                debugfile.write(str(option))

            # extract hover
            option = option.split('[hover]')
            if debug: 
                debugfile.write('\noption[0]: ')
                debugfile.write(str(option[0]))
            hover = ''
            if len(option) == 2:
                hover = option[1]
                if debug: 
                    debugfile.write('\nhover: ')
                    debugfile.write(str(option[1]))

            choice = Choice(text=option[0], hover=hover, inventory=inv)
            choice.save()
            inv.yellow_choices.add(choice)

        # get green choices
        line = file.readline().rstrip()
        if watch:
            print(line)
        options = line.split(';')
        for option in options:
            if watch:
                print(option)
            if debug: 
                debugfile.write('\noption: ')
                debugfile.write(str(option))

            # extract hover
            option = option.split('[hover]')
            if debug: 
                debugfile.write('\noption[0]: ')
                debugfile.write(str(option[0]))
            hover = ''
            if len(option) == 2:
                hover = option[1]
                if debug: 
                    debugfile.write('\nhover: ')
                    debugfile.write(str(option[1]))

            choice = Choice(text=option[0], hover=hover, inventory=inv)
            choice.save()
            inv.green_choices.add(choice)
    else:
        print('error: [choices] tag missing')
        sys.exit(0)

else:
    print('error: [inventory] tag missing')
    sys.exit(0)

# load categories and topics
line = file.readline().rstrip()
if watch:
    print(line)
while line != '':

    if line == '[category]':
        
        # init a category
        line = file.readline().rstrip()
        if watch:
            print(line)
        name = line.split('[hover]')
        if debug: 
            debugfile.write('\ncategory: ')
            debugfile.write(str(name[0]))
        hover = ''
        if len(name) == 2:
            hover = name[1]
            if debug:
                debugfile.write('\nhover: ')
                debugfile.write(str(name[1]))
        cat = Category(type=name[0], hover=hover, inventory=inv)
        cat.save()
        inv.categories.add(cat)

        if debug:
            debugfile.write('\ncreate category: ')
            debugfile.write(cat.type)

        # get the topics
        line = file.readline().rstrip()
        if watch:
            print(line)
        if line == '[topics]':
            count = 1 
            while line != '[category]':
                if line == '[topics]':
                    line = file.readline().rstrip()
                    if watch:
                        print(line)
                    if debug:  
                        debugfile.write('\nline: ')
                        debugfile.write(str(line))
                if line == '':
                    if debug:
                        debugfile.write('\nDone.')
                    if watch:
                        print('Done.')
                    break

                # load the topics
                topics = []
                name = line.split('[hover]')
                if debug: 
                    debugfile.write('\ntopic: ')
                    debugfile.write(str(count) + ' - ' + str(name[0]))
                hover = ''
                if len(name) == 2:
                    hover = name[1]
                    if debug: 
                        debugfile.write('\nhover: ')
                        debugfile.write(str(count) + ' - ' + str(name[1]))
                
                # if 'values' - get name2 and hover2
                name2 = ''
                hover2 = ''
                if inv.type == 'values':
                    line = file.readline().rstrip()
                    if watch:
                        print('values line: ', line)
                    if debug: 
                        debugfile.write('\nvalues line: ')
                        debugfile.write(line)
                    topic2 = line.split('[hover]')
                    if len(topic2) == 2:
                        name2 = topic2[0]
                        hover2 = topic2[1]
                        if debug: 
                            debugfile.write('\nhover2: ')
                            debugfile.write(str(count) + ' - ' + str(hover2))

                # save the topic
                top = Topic(name=name[0], hover=hover, name2=name2,
                            hover2=hover2, category=cat)
                top.save()
                cat.topics.add(top)
                line = file.readline().rstrip()
                if watch:
                    print(line)
                if debug:
                    debugfile.write('\nline: ')
                    debugfile.write(str(line))
                count = count+1

if debug:
    debugfile.close()
sys.exit(0)