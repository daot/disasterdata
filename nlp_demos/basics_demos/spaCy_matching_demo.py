# Have spacy pip installed or conda installed
import spacy
nlp = spacy.load('en_core_web_sm')


# Import the Matcher from spacy
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab) # Create the matcher object

# Define patterns we want to detect, in this example:
# SolarPower
# Solar-Power
# Solar Power
pattern1 = [{'LOWER':'solarpower'}] # Detects SolarPower
pattern2 = [{'LOWER':'solar'},{'IS_PUNCT':True},{'LOWER':'power'}] # Detects Solar-Power
pattern3 = [{'LOWER':'solar'},{'LOWER':'power'}] # Detects Solar Power
matcher.add('SolarPower',[pattern1,pattern2,pattern3]) # Note the match can be called anything but should be relevant


# Now testing with a doc
doc = nlp(u'The Solar Power industry continues to grow as solarpower increases. Solar-power is amazing.')
print(doc)
found_matches = matcher(doc)

# Printing the matches found:
for match_id, start, end in found_matches:
    string_id = nlp.vocab.strings[match_id]
    span = doc[start:end]
    print(f"{match_id:<22} {string_id:12} {start:<3} {end:<3} {span.text:12}")


# Now if we want to remove patterns from the matcher
matcher.remove('SolarPower')

# New patterns
pattern1 = [{'LOWER':'solarpower'}] # Detects SolarPower
pattern2 = [{'LOWER':'solar'},{'IS_PUNCT':True, 'OP':'*'},{'LOWER':'power'}] # Detects Solar-Power or Solar----Power, etc.
matcher.add('SolarPower',[pattern1,pattern2])

# Testing with a new doc
doc2 = nlp(u'Solar---power is solar-power. I love solarpower!')
print(doc2)
found_matches = matcher(doc2)

# Printing the matches found:
for match_id, start, end in found_matches:
    string_id = nlp.vocab.strings[match_id]
    span = doc2[start:end]
    print(f"{match_id:<22} {string_id:12} {start:<3} {end:<3} {span.text:12}")


# Now using a phrase matcher
from spacy.matcher import PhraseMatcher
matcher = PhraseMatcher(nlp.vocab)

# Using a file test as our doc object
with open('../TextFiles/reaganomics.txt',encoding="utf8",errors='ignore') as f:
    doc3 = nlp(f.read())
phrase_list = ['voodoo economics', 'supply-side economics', 'trickle-down economics', 'free-market economics']
phrase_patterns = [nlp(text) for text in phrase_list]

# Add the phrase patterns to the matcher
matcher.add('EconMatcher', phrase_patterns)

# Use the constructed phrase matcher with the file text
found_matches = matcher(doc3)
for match_id, start, end in found_matches:
    string_id = nlp.vocab.strings[match_id]
    span = doc3[start:end]
    print(f"{match_id:<22} {string_id:12} {start:<5} {end:<5} {span.text}")


# If we want to see some context with our matches, modify the for-loop like this:
for match_id, start, end in found_matches:
    string_id = nlp.vocab.strings[match_id]
    span = doc3[start-5:end+5]
    print(f"{match_id:<22} {string_id:12} {start:<5} {end:<5} {span.text}")





