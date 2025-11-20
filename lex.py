DIGITS_AND_SIGN = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-"]


class tok:
    def __init__(self) -> None:
        self.type = ""
        self.val: str | int = ""


class lexer:
    def __init__(self, in_str) -> None:
        self.input_str = in_str
        self.char_index = 0
        self.eol = False
        self.current_char = self.input_str[0]
        self.lookahead_tok = self.get_tok()
        curr = tok()
        curr.type = "BEGIN"
        self.curr_tok = curr

    def __advance_char(self):
        self.char_index += 1
        if self.char_index >= len(self.input_str):
            self.eol = True
            self.current_char = "*"
            # TODO: This is gross, there is certainly a better way to do this. Learn how to write a proper lexer.
            return
        # TODO: verbose exception syntax
        self.current_char = self.input_str[self.char_index]

    def get_tok(self):
        """Attempt to parse a new token using self.input_str as the string of input."""

        # advance past whitespace
        while not self.eol and self.current_char.isspace():
            self.__advance_char()

        ret = tok()

        if self.eol:
            ret.type = "EOL"
            return ret

        # We are now at the start of input
        # brackets
        if self.current_char == "[":
            self.__advance_char()
            ret.type = "LBRACKET"
            return ret
        elif self.current_char == "]":
            self.__advance_char()
            ret.type = "RBRACKET"
            return ret
        # semicolon
        elif self.current_char == ";":
            self.__advance_char()
            ret.type = "SEMICOLON"
            return ret
        # semicolon
        elif self.current_char == ":":
            self.__advance_char()
            ret.type = "COLON"
            return ret
        # period
        elif self.current_char == ".":
            self.__advance_char()
            ret.type = "PERIOD"
            return ret
        # bang
        elif self.current_char == "!":
            self.__advance_char()
            ret.type = "BANG"
            return ret
        # comma
        elif self.current_char == ",":
            self.__advance_char()
            ret.type = "COMMA"
            return ret
        # register literal
        elif self.current_char == "%":
            self.__advance_char()
            reg_name = self.current_char
            self.__advance_char()
            reg_name += self.current_char
            self.__advance_char()
            ret.type = "REGISTER"
            ret.val = reg_name.upper()
            return ret
        # hex literal
        elif self.current_char == "$":
            self.__advance_char()
            num = ""
            while self.current_char.isalnum():
                num += self.current_char
                self.__advance_char()
            ret.type = "NUMBER"
            ret.val = int(num, 16)
            return ret
        # integer literal
        elif self.current_char == "#":
            self.__advance_char()
            num = ""
            while self.current_char in DIGITS_AND_SIGN:
                num += self.current_char
                self.__advance_char()
            ret.type = "NUMBER"
            ret.val = int(num, 10)
            return ret
        # String of any sort
        elif self.current_char.isidentifier():
            string = ""
            while self.current_char.isidentifier():
                string += self.current_char
                self.__advance_char()
            ret.type = "IDENTIFIER"
            ret.val = string
            return ret
        elif self.current_char == '"':
            string = ""
            self.__advance_char()
            while not self.current_char == '"':
                if self.eol:
                    raise EOFError("Error: Encountered EOL while trying to parse string!")
                string += self.current_char
                self.__advance_char()
            self.__advance_char()
            ret.type = "STRING"
            ret.val = string
            return ret
        else:
            raise SyntaxError(
                "Un-Handleable char in input stream. The char was %s"
                % self.current_char
            )

    def advance(self):
        self.curr_tok = self.lookahead_tok
        self.lookahead_tok = self.get_tok()
