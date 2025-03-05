from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    NOTE = auto()  # C4, D#3, etc.
    DURATION = auto()  # 1/4, 1/8, etc.
    TEMPO = auto()  # tempo keyword
    TIME = auto()  # time keyword
    NUMBER = auto()  # Any number
    SLASH = auto()  # /
    SEQUENCE = auto()  # sequence keyword
    IDENTIFIER = auto()  # sequence names, etc.
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    CHANNEL = auto()  # channel keyword
    VELOCITY = auto()  # velocity keyword
    PLAY = auto()  # play keyword
    REST = auto()  # R (rest)
    NEWLINE = auto()  # \n
    EOF = auto()  # End of file


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.current_char = (
            self.source[self.current] if self.current < len(self.source) else None
        )
        self.last_token_type: Optional[TokenType] = None

    def error(self) -> None:
        raise Exception(
            f"Invalid character {self.current_char} at line {self.line}, "
            f"column {self.column}"
        )

    def advance(self) -> Optional[str]:
        self.current += 1
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.current_char = (
            self.source[self.current] if self.current < len(self.source) else None
        )
        return self.current_char

    def skip_whitespace(self) -> None:
        while (
            self.current_char
            and self.current_char.isspace()
            and self.current_char != "\n"
        ):
            self.advance()

    def skip_comment(self) -> None:
        while self.current_char and self.current_char != "\n":
            self.advance()

    def number(self) -> Token:
        result = ""
        start_column = self.column

        # Read the first number
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        # Check for duration or time signature
        if self.current_char == "/":
            # Always return the number first
            token = Token(TokenType.NUMBER, result, self.line, start_column)
            self.last_token_type = token.type
            return token

        token = Token(TokenType.NUMBER, result, self.line, start_column)
        self.last_token_type = token.type
        return token

    def identifier(self) -> Token:
        result = ""
        start_column = self.column

        while self.current_char and (
            self.current_char.isalnum() or self.current_char in "#b_"
        ):
            result += self.current_char
            self.advance()

        # Check for keywords
        keywords = {
            "tempo": TokenType.TEMPO,
            "time": TokenType.TIME,
            "sequence": TokenType.SEQUENCE,
            "channel": TokenType.CHANNEL,
            "velocity": TokenType.VELOCITY,
            "play": TokenType.PLAY,
            "R": TokenType.REST,
        }

        # Check if it's a note (e.g., C4, D#3, Bb4)
        if len(result) >= 2 and result[0].upper() in "ABCDEFG" and result[-1].isdigit():
            token = Token(TokenType.NOTE, result, self.line, start_column)
        else:
            token = Token(
                keywords.get(result, TokenType.IDENTIFIER),
                result,
                self.line,
                start_column,
            )

        self.last_token_type = token.type
        return token

    def get_next_token(self) -> Token:
        if not self.current_char:
            return Token(TokenType.EOF, "", self.line, self.column)

        self.skip_whitespace()

        if not self.current_char:
            return Token(TokenType.EOF, "", self.line, self.column)

        start_column = self.column

        # Handle newlines
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
            self.advance()
            token = Token(TokenType.NEWLINE, "\n", self.line - 1, start_column)
            self.last_token_type = token.type
            return token

        # Handle numbers and durations
        if self.current_char.isdigit():
            return self.number()

        # Handle slash (for durations and time signatures)
        if self.current_char == "/":
            self.advance()
            token = Token(TokenType.SLASH, "/", self.line, start_column)
            self.last_token_type = token.type
            return token

        if self.current_char.isalpha() or self.current_char in "#b_":
            return self.identifier()

        if self.current_char == "{":
            self.advance()
            token = Token(TokenType.LBRACE, "{", self.line, self.column - 1)
            self.last_token_type = token.type
            return token

        if self.current_char == "}":
            self.advance()
            token = Token(TokenType.RBRACE, "}", self.line, self.column - 1)
            self.last_token_type = token.type
            return token

        if self.current_char == "[":
            self.advance()
            token = Token(TokenType.LBRACKET, "[", self.line, self.column - 1)
            self.last_token_type = token.type
            return token

        if self.current_char == "]":
            self.advance()
            token = Token(TokenType.RBRACKET, "]", self.line, self.column - 1)
            self.last_token_type = token.type
            return token

        # If we get here, we have an invalid character
        self.error()
        return Token(TokenType.EOF, "", self.line, self.column)  # For type checker

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

    def peek(self) -> Optional[str]:
        if self.current >= len(self.source):
            return None
        return self.source[self.current]
