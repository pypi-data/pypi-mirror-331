import string

class PakEngTag:
    def __init__(self):
        # Define a dictionary of unique Pakistani English and British English words with their tags
        self.unique_words = {
            'sharifs': 'N_Fam_PK',
            'sabeel': 'N_Reg_PK',
            'istehkam': 'N_PK',
            'chaki': 'N_Mac_PK',
            'kiani': 'N_Cst_PK',
            'ashura': 'N_Reg_PK',
            'majalis': 'N_PK',
            'karzai': 'N_Cst_PK',
            'tarar': 'N_Cst_PK',
            'barelvi': 'N_Sect_PK',
            'jihad': 'N_Reg_PK',
            'jalili': 'N_Cst_PK',
            'alvi': 'N_Cst_PK',
            'iddat': 'N(Religious)-PK-O',
            # British English words
            'love': 'VERB-BR',
            'cast': 'NOUN-BR',
            'family': 'NOUN-BR',
            'child': 'NOUN-BR',
            'man': 'NOUN-BR',
            'woman': 'NOUN-BR',
            'person': 'NOUN-BR',
            'friend': 'NOUN-BR',
            'house': 'NOUN-BR',
            'car': 'NOUN-BR',
            'dog': 'NOUN-BR',
            'cat': 'NOUN-BR',
            'food': 'NOUN-BR',
            'time': 'NOUN-BR',
            'place': 'NOUN-BR',
            'work': 'NOUN-BR',
            'thing': 'NOUN-BR',
            'way': 'NOUN-BR',
            'country': 'NOUN-BR',
            'year': 'NOUN-BR',
            'government': 'NOUN-BR',
            'school': 'NOUN-BR',
            'health': 'NOUN-BR',
            'market': 'NOUN-BR',
            'business': 'NOUN-BR',
            'day': 'NOUN-BR',
            'police': 'NOUN-BR',
            'hand': 'NOUN-BR',
            'heart': 'NOUN-BR',
            'city': 'NOUN-BR',
            'money': 'NOUN-BR',
            'team': 'NOUN-BR',
            'life': 'NOUN-BR',
            'problem': 'NOUN-BR',
            'fact': 'NOUN-BR',
            'story': 'NOUN-BR',
            'book': 'NOUN-BR',
            'idea': 'NOUN-BR',
            'moment': 'NOUN-BR',
            'quality': 'NOUN-BR',
            'service': 'NOUN-BR',
            'area': 'NOUN-BR',
            'choice': 'NOUN-BR',
            'voice': 'NOUN-BR',
            'job': 'NOUN-BR',
            'member': 'NOUN-BR',
            'father': 'NOUN-BR',
            'mother': 'NOUN-BR',
            'brother': 'NOUN-BR',
            'sister': 'NOUN-BR',
            'partner': 'NOUN-BR',
            'childhood': 'NOUN-BR',
            'class': 'NOUN-BR',
            'name': 'NOUN-BR',
            'power': 'NOUN-BR',
            'process': 'NOUN-BR',
            'nature': 'NOUN-BR',
            'culture': 'NOUN-BR',
            'interest': 'NOUN-BR',
            'opportunity': 'NOUN-BR',
            'event': 'NOUN-BR',
            'situation': 'NOUN-BR',
            'relationship': 'NOUN-BR',
            'company': 'NOUN-BR',
            'purpose': 'NOUN-BR',
            'art': 'NOUN-BR',
            'history': 'NOUN-BR',
            'friendship': 'NOUN-BR',
            'experience': 'NOUN-BR',
            'movement': 'NOUN-BR',
            'goal': 'NOUN-BR',
            'technology': 'NOUN-BR',
            'development': 'NOUN-BR',
            'community': 'NOUN-BR',
            'state': 'NOUN-BR',
            'project': 'NOUN-BR',
            'truth': 'NOUN-BR',
            'region': 'NOUN-BR',
            'decision': 'NOUN-BR',
            'building': 'NOUN-BR',
            'access': 'NOUN-BR',
            'response': 'NOUN-BR',
            'mission': 'NOUN-BR',
            'source': 'NOUN-BR',
            'travel': 'NOUN-BR',
            'condition': 'NOUN-BR',
            'example': 'NOUN-BR',
            'study': 'NOUN-BR',
        }

        # Define rules for general tagging
        self.noun_endings = ('tion', 's', 'ment', 'ness', 'ity', 'age', 'ing')
        self.verb_endings = ('ed', 'ing', 's')
        self.adjective_endings = ('ful', 'ous', 'able', 'ive', 'y')
        self.adverb_endings = ('ly',)

        # Define lists for prepositions and conjunctions
        self.prepositions = ['in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down']
        self.conjunctions = ['and', 'but', 'or', 'nor', 'for', 'so', 'yet', 'although', 'because', 'since', 'unless', 'while', 'whereas']

    def tag_word(self, word):
        # Remove punctuation and convert to lowercase
        stripped_word = word.strip(string.punctuation).lower()

        # Check for unique words
        if stripped_word in self.unique_words:
            return (word, self.unique_words[stripped_word])
        
        # General rules for tagging
        if stripped_word in ['he', 'she', 'it', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'them', 'my', 'your', 'his', 'its', 'our']:
            return (word, 'PRONOUN')  # Pronouns
        elif any(stripped_word.endswith(ending) for ending in self.noun_endings):
            return (word, 'NOUN')  # Nouns
        elif any(stripped_word.endswith(ending) for ending in self.verb_endings):
            return (word, 'VERB')  # Verbs
        elif any(stripped_word.endswith(ending) for ending in self.adjective_endings):
            return (word, 'ADJECTIVE')  # Adjectives
        elif any(stripped_word.endswith(ending) for ending in self.adverb_endings):
            return (word, 'ADVERB')  # Adverbs
        elif stripped_word.isdigit():  # Check if the word is a number
            return (word, 'NUMBER')  # Numbers
        elif stripped_word in self.conjunctions:
            return (word, 'CONJUNCTION')  # Conjunctions
        elif stripped_word in self.prepositions:
            return (word, 'PREPOSITION')  # Prepositions
        elif stripped_word in ['a', 'an', 'the', 'this', 'that', 'these', 'those']:
            return (word, 'DETERMINER')  # Determiners

        return (word, 'UNKNOWN')  # Default tag if not found

    def tag_sentence(self, sentence):
        words = sentence.split()  # Split the sentence into words
        tagged_words = [self.tag_word(word) for word in words]
        return tagged_words
