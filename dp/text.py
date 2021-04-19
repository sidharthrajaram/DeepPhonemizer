from typing import List, Iterable, Dict, Tuple, Any


class LanguageTokenizer:

    def __init__(self, languages: List[str]) -> None:
        self.lang_index = {l: i for i, l in enumerate(languages)}
        self.index_lang = {i: l for i, l in enumerate(languages)}

    def __call__(self, lang: str) -> int:
        return self.lang_index[lang]

    def decode(self, index: int) -> str:
        return self.index_lang[index]


class SequenceTokenizer:

    def __init__(self,
                 symbols: List[str],
                 languages: List[str],
                 lowercase=True,
                 append_start_end=True,
                 pad_token='_',
                 end_token='<end>') -> None:
        self.lowercase = lowercase
        self.append_start_end = append_start_end
        self.pad_index = 0
        self.token_to_idx = {pad_token: self.pad_index}
        self.special_tokens = {pad_token, end_token}
        for lang in languages:
            lang_token = '<' + lang + '>'
            self.token_to_idx[lang_token] = len(self.token_to_idx)
            self.special_tokens.add(lang_token)
        self.token_to_idx[end_token] = len(self.token_to_idx)
        self.end_index = self.token_to_idx[end_token]
        for symbol in symbols:
            self.token_to_idx[symbol] = len(self.token_to_idx)
        self.idx_to_token = {i: s for s, i in self.token_to_idx.items()}
        self.vocab_size = len(self.idx_to_token)

    def __call__(self, sentence: Iterable[str], language: str) -> List[int]:
        if self.lowercase:
            sentence = [s.lower() for s in sentence]
        sequence = [self.token_to_idx[c] for c in sentence if c in self.token_to_idx]
        if self.append_start_end:
            sequence = [self.get_start_index(language)] + sequence + [self.end_index]
        return sequence

    def decode(self, sequence: Iterable[int], remove_special_tokens=False) -> List[str]:
        decoded = [self.idx_to_token[int(t)] for t in sequence if int(t) in self.idx_to_token]
        if remove_special_tokens:
            decoded = [d for d in decoded if d not in self.special_tokens]
        return decoded

    def get_start_index(self, language: str) -> int:
        return self.token_to_idx['<' + language + '>']


class Preprocessor:

    def __init__(self,
                 lang_tokenizer: LanguageTokenizer,
                 text_tokenizer: SequenceTokenizer,
                 phoneme_tokenizer: SequenceTokenizer) -> None:
        self.lang_tokenizer = lang_tokenizer
        self.text_tokenizer = text_tokenizer
        self.phoneme_tokenizer = phoneme_tokenizer

    def __call__(self,
                 item: Tuple[str, Iterable[str], Iterable[str]]):

        lang, text, phonemes = item
        lang_token = self.lang_tokenizer(lang)
        text_tokens = self.text_tokenizer(text, lang)
        phoneme_tokens = self.phoneme_tokenizer(phonemes, lang)
        return lang_token, text_tokens, phoneme_tokens

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Preprocessor':
        text_symbols = config['preprocessing']['text_symbols']
        phoneme_symbols = config['preprocessing']['phoneme_symbols']
        lang_symbols = config['preprocessing']['languages']
        lowercase = config['preprocessing']['lowercase']
        lang_tokenizer = LanguageTokenizer(lang_symbols)
        text_tokenizer = SequenceTokenizer(symbols=text_symbols,
                                           languages=lang_symbols,
                                           lowercase=lowercase,
                                           append_start_end=True)
        phoneme_tokenizer = SequenceTokenizer(phoneme_symbols,
                                              languages=lang_symbols,
                                              lowercase=lowercase,
                                              append_start_end=True)
        return Preprocessor(lang_tokenizer=lang_tokenizer,
                            text_tokenizer=text_tokenizer,
                            phoneme_tokenizer=phoneme_tokenizer)
