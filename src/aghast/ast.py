class BaseNode:
    def __init__(self, tokens):
        self.tokens = tokens


class ImportStatement(BaseNode):
    def __init__(self, tokens, module_section, imports):
        super().__init__(tokens)

        self.module_section = module_section
        self.imports = imports


class ImportModuleSection(BaseNode):
    def __init__(self, tokens, local, local_index, modules):
        super().__init__(tokens)

        self.local = local
        self.local_index = local_index
        self.modules = modules


class SingleImport(BaseNode):
    def __init__(self, tokens, import_name, alias):
        super().__init__(tokens)

        self.import_name = import_name
        self.alias = alias
