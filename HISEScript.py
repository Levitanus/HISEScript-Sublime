import sublime
import sublime_plugin
import re

classes = list()


def add(string, ident):
    ident_str = '    '
    if isinstance(string, str):
        return '\n' + ident_str * ident + string
    out = ''
    for item in string:
        out += '\n' + ident_str * ident + item
    return out


class ApiMethod:

    def __init__(self, decl_line, doc):
        self.doc = self.clean_doc(doc)
        self.parce(decl_line)

    def parce(self, line):
        # print(line)
        m = re.match(
            r'(?P<return>.+?)\s?\*?(?P<name>\w+?)\((?P<tokens>.*?)\)', line)
        self.name = m.group('name')
        self.tokens = re.sub(r'&|(const)', '', m.group('tokens')).strip()
        self.return_value = m.group('return')

    def clean_doc(self, doc):
        out = list()
        for line in doc:
            line = re.sub(r'/\*\*', '', line)
            # line = re.sub(r'\S', '', line)
            line = re.sub(r'\*/', '', line)
            line = re.sub(r'\*', '', line)
            line = line.strip()
            if line:
                out.append(line)
        return out

    def __str__(self):
        out = ''
        out += add('%s(%s) -> %s' %
                   (self.name, self.tokens, self.return_value), 0)
        out += add(self.doc, 1)
        return out[1:]


class ApiClass:

    def __init__(self, name):
        self.name = re.match(
            r'((class)|(struct)) (?P<class>\w+?)\b',
            name).group('class').strip()
        # print(self.name)
        self.methods = list()

    def __str__(self):
        out = self.name

        for method in self.methods:
            out += add(str(method).split('\n'), 1)
            out += '\n'
        return out


def parce_core_classes(lines):
    classes = list()
    curr_clas = str()
    count = 0
    doc = 0
    docbody = list()
    for line in lines:
        line = line.strip()
        if line.startswith("class"):
            curr_clas = line
            count = 0
        if line.find("// ======") != -1:
            count += 1
            if count == 2:
                classes.append(ApiClass(curr_clas))
        if count == 2:
            if doc == -1:
                doc = 0
                classes[-1].methods.append(ApiMethod(line, docbody))
            if line.startswith('/**'):
                doc = 1
                docbody = list()
            if doc == 1:
                docbody.append(line)
            if line.find('*/') != -1 and doc == 1:
                doc = -1
    return classes


def parce_content_classes(lines):
    classes = list()
    curr_clas = str()
    count = 0
    doc = 0
    docbody = list()
    content_class = False
    for line in lines:
        line = line.strip()
        if line.startswith('Content(ProcessorWithScripting'):
            curr_clas = 'struct Content:'
            classes.append(ApiClass(curr_clas))
            content_class = True
            count = 0
        if line.startswith("struct"):
            # print("line.startswith(struct):")
            curr_clas = line
            count = 0
        if line.find(" ======") != -1:
            # print("line.find(' ======') != -1 and count == 1:")
            if count == 1:
                count = 0
            if content_class:
                count = 1
        if re.search('api methods', line, re.I):
            # print("re.search('api methods', line, re.I)")
            # print(curr_clas)
            classes.append(ApiClass(curr_clas))
            count = 1
        if count == 1:
            # print("count == 1:")
            if doc == -1:
                doc = 0
                classes[-1].methods.append(ApiMethod(line, docbody))
            if line.startswith('/**'):
                doc = 1
                docbody = list()
            if doc == 1:
                docbody.append(line)
            if line.find('*/') != -1:
                doc = -1
    return classes


def parce_object_classes(lines):
    classes = list()
    curr_clas = str()
    count = 0
    doc = 0
    docbody = list()
    for line in lines:
        line = line.strip()
        if line.startswith("class"):
            curr_clas = line
            count = 0
        if line.find("// ======") != -1:
            count += 1
            if count == 2:
                # print(curr_clas)
                classes.append(ApiClass(curr_clas))
        if count >= 2:
            if doc == -1:
                doc = 0
                if re.match(
                        r'(?P<return>.+?)\s?\*?(?P<name>\w+?)\(' +
                        r'(?P<tokens>.*?)\)', line):
                    # print('valid line:' + line)
                    classes[-1].methods.append(ApiMethod(line, docbody))
            if line.startswith('/**'):
                doc = 1
                docbody = list()
            if doc == 1:
                docbody.append(line)
            if line.find('*/') != -1:
                doc = -1
    return classes


class HiseCompletion(sublime_plugin.EventListener):
    is_class = object()
    is_object = object()

    def on_query_completions(self, view, prefix, locations):
        scope = view.scope_name(locations[0] - 1)
        if scope.find("source.js") == -1:
            return
        if prefix == '':
            if view.substr(locations[0] - 1) == '.':
                prefix = view.substr(view.word(locations[0] - 1))
        out = list()
        # out.append(['name\tright','completion ${1:first} and $2second'])
        print(scope)
        for clas in classes:
            for method in clas.methods:
                is_class = False
                if clas.name.startswith(prefix):
                    is_class = True
                if method.name.find(prefix) != -1:
                    if scope.find('variable') != -1:
                        is_class = True
                out.append(
                    self.make_completion(clas, method, is_class))
        return out

    def make_completion(self, clas, method, is_class):
        tokens_list = method.tokens.split(',')
        # print(tokens_list)
        tokens = list()
        for idx, token in enumerate(tokens_list):
            tokens.append('${%s:%s}' % (
                idx + 1, token.strip()))
        tokens = ','.join(tokens)
        # print(tokens)
        trigger = "{name}\t{clas}: HISE".format(
            clas=clas.name,
            name=method.name)
        content = '{name}({tokens})'.format(
            name=method.name,
            tokens=tokens)
        out = list()
        if is_class:
            for item in (trigger, content):
                out.append(clas.name + '.' + item)
        else:
            out = [trigger, content]
        # print(out)
        return out


class HiseShowDocCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        word = self.view.substr(self.view.word(self.view.sel()[0].begin()))
        for clas in classes:
            for method in clas.methods:
                if word == method.name:
                    message = self.draw_method_doc(clas, method)
                    self.view.show_popup(message,
                                         sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                                         -1, 600, 200, lambda: None,
                                         lambda: None)
                    return

    def draw_method_doc(self, clas, method):
        doc = '<br>'.join(method.doc)
        out = """
        <b>{clas}</b>.{name}(<em>{tokens}</em>) ->
        <em>{return_value}</em><br><br>{doc}
        """.format(
            clas=clas.name,
            name=method.name,
            tokens=method.tokens,
            return_value=method.return_value,
            doc=doc)
        return out


# hise_path = 'C:/HISE-master'

def error():
    return sublime.error_message(
        '''Wrong HISE path. Put to the settings a valid HISE path.
        C:/HISE-master, for example''')


def plugin_loaded():
    settings = sublime.load_settings('HISEScript.sublime-settings')
    hise_path = settings.get('hise_path')
    print(settings)
    print(settings.has('hise_path'))
    print(hise_path)
    try:
        api_path = hise_path + '/hi_scripting/scripting/api/'
    except TypeError:
        error()
        # classes = list()
    core_path = api_path + 'ScriptingApi.h'
    content_path = api_path + 'ScriptingApiContent.h'
    objects_path = api_path + 'ScriptingApiObjects.h'

    try:
        with open(core_path, 'r') as f:
            core = f.readlines()
    except FileNotFoundError:
        error()
    with open(content_path, 'r') as f:
        content = f.readlines()
    with open(objects_path, 'r') as f:
        objects = f.readlines()

    global classes
    classes = list()
    classes.extend(parce_core_classes(core))
    classes.extend(parce_content_classes(content))
    classes.extend(parce_object_classes(objects))


class HiseReloadCommand(sublime_plugin.WindowCommand):
    def run(self):
        plugin_loaded()
