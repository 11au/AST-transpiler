#!/usr/bin/python3 -u
import sys
import re
# AST node classes
class Echo:
    def __init__(self, name, arguments):
        self.name = name # echo 
        self.arg = arguments
class Shebang:
    def __init__(self, name):
        self.name = name # shebang statement
class Newline:
    def __init__(self, name):
        self.name = name
class Variable: 
    def __init__(self, name, variable_name, variable_value ):
        self.name = name
        self.variable_name = variable_name
        self.variable_value = variable_value
class Reference:
    def __init__(self, name, variable_value):
        self.name = name
        self.variable_value= variable_value
class cd: 
    def __init__(self, name, location):
        self.name = name 
        self.location = location
class pwd:
    def __init__(self, name):
        self.name = name
class For:
    def __init__(self, name, item, sequence):
        self.name = name
        self.item = item
        self.sequence = sequence
# lexer - tokenises each word in a tuple with corresponding type
def lexer(content):
    shell_lines = content.split("\n")
    tokens=[]
    for line in shell_lines:
        for word in line.split():
            if word.startswith("#!"):
                tokens.append(("SHEBANG", word))
            elif word == "echo":
                tokens.append(("KEYWORD", word))
            elif "=" in word: # ADD PROPER REGEX FOR setting variable
                tokens.append(("ASSIGN", word))
            elif word.startswith("$"):
                tokens.append(("REFERENCE", word, word[1:]))
            elif word == "cd":
                tokens.append(("KEYWORD", word))
            elif word == "pwd":
                tokens.append(("KEYWORD", word))
            elif word == "for":
                tokens.append(("KEYWORD", word))
            elif word == "in":
                tokens.append(("KEYWORD", word))
            elif word == "do":
                tokens.append(("KEYWORD", word))
            elif word == "done":
                tokens.append(("KEYWORD", word))                
            else:
                tokens.append(("WORD", word))
        tokens.append(("NEWLINE", "\n"))
    return tokens

# parser - parses the tokens and produces a AST
def parser(tokens):
    AST = []
    index = 0
    while index < len(tokens):
        kind = tokens[index][0]
        name = tokens[index][1]
        if (kind == "SHEBANG"):
            AST.append(Shebang(name))
        elif (kind == "KEYWORD" and name == "echo"):
            index += 1
            arguments = []
            while index < len(tokens) and tokens[index][0] != "NEWLINE":
                # if variable then evaluate by finding the variable 
                argument = tokens[index][1]
                arguments.append(argument)
                index += 1
            AST.append(Echo(name,arguments))
            continue
        elif (kind == "KEYWORD" and name == "cd"):
            index += 1
            if (index < len(tokens)):
                file_path = tokens[index][1]
                AST.append(cd(name, file_path))
                index += 1
        elif (kind == "KEYWORD" and name == "pwd"):
            AST.append(pwd(name))
        elif (kind == "KEYWORD" and name == "for"):
            index += 1 
            item = tokens[index][1]
            sequence = []
            while index < len(tokens) and tokens[index][0] != "KEYWORD" and tokens[index][1] != "do":
                sequence.append(tokens[index][1])
            AST.append(For(name, item, sequence))
        elif (kind == "NEWLINE"):
            AST.append(Newline(name))
        elif (kind == "ASSIGN"):
            var = Variable(name, name.split("=")[0], name.split("=")[1])
            AST.append(var)
        elif (kind == "REFERENCE"):
            AST.append(Reference(name))
        
        index += 1
    return AST

# evaluator - translates AST
def evaluator(AST):
    # indentation
    indents = 0
    # shebang
    shebang = ""
    # python imports
    imports = set()
    # python output
    body = ""
    for node in AST:
        if isinstance(node, Shebang):
            shebang += ("#!/usr/bin/python3 -u")
            shebang += "\n" # this determines the new line need to change this
        elif isinstance(node, Newline):
            body += (node.name)
        elif isinstance(node, Echo):
            containsRefs = False;
            arg_formatted = []
            for arg in node.arg:
                if arg.startswith("$"):
                    containsRefs = True
                    arg_formatted.append("{"+arg[1:]+"}")
                else:
                    arg_formatted.append(arg)
            if containsRefs:
                body += "print(f'"+' '.join(arg_formatted)+"')"
            else:
                body += "print('"+' '.join(arg_formatted)+"')"
        elif isinstance(node, Variable):
            body += node.variable_name+' = '+node.variable_value
        # elif isinstance(node, Reference):
        #     body +=
        elif isinstance(node, cd):
            imports.add("os")
            body += "os.chdir('"+node.location+"')"
        elif isinstance(node, pwd):
            imports.add("subprocess")
            body += "subprocess.run(['"+node.name+"'])"
    formatted_imports = set(map(lambda x: "import "+x, imports))
    # handles extra line 
    body = body.removesuffix("\n")
    body = shebang+"\n".join(formatted_imports)+body
    print(body)
                

# Main 
script_path = sys.argv[1]
with open(script_path, "r") as file:
    content = file.read()

tokens = lexer(content)
AST = parser(tokens)
# print(AST)
evaluator(AST)
