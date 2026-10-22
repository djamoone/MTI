import sys 
import re #regular experssion


def clean_text(text):
    # Remove punctuation from a text
    # Replaces defined punctuation characters with an empty string
    punct = "  +.*/?,; \\ ' #"
    for p in punct:
        text = text.replace(p, "")
    return text


def tokenize(text):
    # Convert text into tokens, return a list of tokens (words)
    return text.split()


def tokenize2(text):
    """Convert text into tokens, return a list of tokens (words)."""
    spaces = r"\s+" # r"..." 
    words = re.split(spaces, text)
    return words


def word_freq(words):
    """Counts words and returns a dictionary of words with their occurrences."""
    index = {}
    for w in words:
        if w in index:
            index[w] += 1
        else:
            index[w] = 1
    return index


def most_common_word(words_freq_table):
    """Finds and returns the most common word in a frequency dictionary."""
    frequent = ""
    frequency = 0
    for word in words_freq_table:
        if words_freq_table[word] > frequency:
            frequent = word
            frequency = words_freq_table[word]
    return frequent


def read_file(filename):
    """Reads text from a file."""
    try:
        f1 = open(filename, "r")
    except Exception:
        print("Can't open file,", filename)
        sys.exit()

    text = f1.read()
    f1.close()
    return text


def main(args):
    text =  "Surprise steepest recurred landlord mr wandered amounted of Continuing devonshire but considered its. Rose past oh shew roof is song neat. Do depend better praise do friend garden an wonder to. Intention age nay otherwise but breakfast. Around garden beyond to extent by."
    

    text1 = clean_text(text)
    print("Cleaned sample text:", text1)

    # Tokenize text
    words = tokenize(text)
    print("\nTokens:", words)

    # Tokenize text
    words = tokenize2(text)
    print("\nTokens:", words)

    
    words_nb = word_freq(words)
    print("\nWord Frequency:", words_nb)

    # Read from external file
    data = read_file("../data.txt")
    print("\nFile Data:", data)

    text = data
    words = tokenize(text)
    print("\nFile Tokens:", words)

    word_freq_table = word_freq(words)
    print("\nFile Word Frequency Table:", word_freq_table)

    freqw = most_common_word(word_freq_table)
    print(
        f"\nMost frequent word is '{freqw}': {word_freq_table.get(freqw, 0)}"
    )

    return 0


if __name__ == "__main__":
    main(sys.argv)