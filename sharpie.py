#!/usr/bin/python3 -u
import sys
import re
# AST node classes
class Word:
    def __init__(self, name):
        self.name = name
class Echo:
    def __init__(self, name, arguments, contains_ref):
        self.name = name # echo 
        self.arg = arguments
        self.contains_ref = contains_ref
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
    def __init__(self, original, name):
        self.original = original
        self.name = name

class cd: 
    def __init__(self, name, location):
        self.name = name 
        self.location = location
class pwd:
    def __init__(self, name):
        self.name = name
class For:
    def __init__(self, name, item, sequence, contains_ref):
        self.name = name
        self.item = item
        self.sequence = sequence
        self.contains_ref = contains_ref
class Exit:
    def __init__(self, name):
        self.name = name
class Do:
    def __init__(self, name):
        self.name = name
class Done:
    def __init__(self, name):
        self.name = name
class Glob:
    def __init__(self, name):
        self.name = name
        self.expanded_name = "sorted(glob.glob("+self.name+"))"

    
# argument collector
def collect_args(tokens, index):
    args = []
    contains_refs = False
    while index < len(tokens) and tokens[index][0] != "NEWLINE":
        kind, name = tokens[index]
        if (kind == "REF"):
            args.append(Reference(name, "{"+name[1:]+"}"))
            contains_refs = True
        if (kind == "WORD"):
            args.append(Word(name))
        index += 1
    return args, index, contains_refs

# lexer - tokenises each word in a tuple with corresponding type
def lexer(content):
    shell_lines = content.split("\n")
    tokens=[]
    for line in shell_lines:
        for word in line.split():
            if word.startswith("#!"):
                tokens.append(("SHEBANG", word))
            elif word.startswith("$"):
                tokens.append(("REF", word))
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
            elif word == "do":
                tokens.append(("KEYWORD", word))
            elif word == "done":
                tokens.append(("KEYWORD", word))    
            elif word == "exit":             
                tokens.append(("KEYWORD", word))
            else:
                tokens.append(("WORD", word))
        # only add line if non-empty
        if line.strip():
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
            arguments, index, contains_ref = collect_args(tokens, index)
            AST.append(Echo(name, arguments, contains_ref))
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
            index += 2 # style
            arguments, index, contains_ref = collect_args(tokens, index)
            AST.append(For(name, item, arguments, contains_ref))
        elif (kind == "KEYWORD" and name == "do"):
            AST.append(Do(name))
        elif (kind == "KEYWORD" and name == "done"):
            AST.append(Done(name))
        elif (kind == "NEWLINE"):
            AST.append(Newline(name))
        elif (kind == "ASSIGN"):
            var = Variable(name, name.split("=")[0], name.split("=")[1])
            AST.append(var)
        elif (kind == "REFERENCE"):
            AST.append(Reference(name))
        elif (kind == "WORD"):
            AST.append(Word(name))
        elif (kind == "KEYWORD" and name == "exit"):
            AST.append(Exit(name))
        index += 1
    return AST

# evaluator - translates AST
def evaluator(AST):
    # indentation
    indents = 0
    tab = "    "
    # shebang
    shebang = ""
    # python imports
    imports = set()
    # python output
    body = ""
    for node in AST:
        body += tab*indents
        if isinstance(node, Shebang):
            shebang += ("#!/usr/bin/python3 -u\n")
            # shebang += "\n" # this determines the new line need to change this
        elif isinstance(node, Newline):
            body += (node.name)
        elif isinstance(node, Echo):
            if (node.contains_ref):
                body += "print(f\"" + ' '.join([arg.name for arg in node.arg]) + "\")"            
            else:
                body += "print(\"" + ' '.join([arg.name for arg in node.arg]) + "\")"
        elif isinstance(node, Variable):
            body += node.variable_name+' = '+node.variable_value
        elif isinstance(node, cd):
            imports.add("os")
            body += "os.chdir('"+node.location+"')"
        elif isinstance(node, pwd):
            imports.add("subprocess")
            body += "subprocess.run(['"+node.name+"'])"
        elif isinstance(node, For):
            body += "for "+ node.item + " in " +"["+", ".join([f"'{node.name}'" for node in node.sequence])+"]:"
        elif isinstance(node, Do):
            indents += 1
        elif isinstance(node, Do):
            indents -= 1
        elif isinstance(node, Exit):
            body += "sys.exit(0)"
            imports.add("sys")
    formatted_imports = set(map(lambda x: "import "+x, imports))
    # handles extra line 
    body = body.removesuffix("\n")
    body = shebang+"\n".join(formatted_imports)+"\n"+body
    return body                

# Main 
script_path = sys.argv[1]
with open(script_path, "r") as file:
    content = file.read()

tokens = lexer(content)
AST = parser(tokens)
body = evaluator(AST)
print(body)
