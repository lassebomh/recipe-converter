
import re
from fractions import Fraction
import unicodedata
from math import floor

units = {

	'metric': {
		'volume': {
			1: ['m^3', 'cubic metre', 'cubic meter'],
			1000: ['l', 'litre', 'liter'],
			10000: ['dl', 'decilitre', 'deciliter'],
			1e+6: ['ml', 'millilitre', 'milliliter'],
		},
		'mass': {
			1: ['kg', 'kilogram'],
			1000: ['g', 'gram'],
			1e+6: ['mg', 'milligram'],
		}
	},
	'us': {
		'volume': {
			264.172: ['liquid gallon', 'gallon'],
			1056.69: ['liquid quart'],
			2113.38: ['liquid pint'],
			4166.67: ['legal cup', 'cup', 'c'],
			33814: ['fluid ounce', 'fl oz'],
			67628: ['tablespoon', 'tbsp', 'tbl', 'tbs','tbsp'],
			202884: ['teaspoon', 'tsp'],
		},
		'mass': {
			2.20462: ['pound', 'lb', '#'],
			35.274: ['ounce', 'oz'],
		}
	}
}

fractions =[
	['½', '⅓', '⅔', '¼', '¾', '⅕', '⅖', '⅗', '⅘', '⅙', '⅚', '⅐', '⅛', '⅜', '⅝', '⅞', '⅑', '⅒'],
	[0.5, 0.3333333333333333, 0.6666666666666666, 0.25, 0.75, 0.2, 0.4, 0.6, 0.8, 0.16666666666666666, 0.8333333333333334, 0.14285714285714285, 0.125, 0.375, 0.625, 0.875, 0.1111111111111111, 0.1]
]

numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

for system in units.keys():
	for unitType in units[system]:
		for unit in units[system][unitType].values():
			newUnits = []
			for rootabbr in unit:
				for abbr in [rootabbr+declension for declension in ['.', 's']]:
					newUnits.append(abbr)
			for newUnit in newUnits:
				unit.append(newUnit)

def masterConvert(recipe, unitFrom, unitTo, fuzzyMath=True):

	recipe = re.sub(r'(\d+)(\w{1,3})', r'\1 \2', recipe)
	recipe = [line.split(' ') for line in recipe.split('\n') if line != '']

	for lineindex, line in enumerate(recipe):
		for wordindex, word in enumerate(line):
			try: recipe[lineindex][wordindex] = fractions[1][fractions[0].index(word)]
			except ValueError: pass
			try: recipe[lineindex][wordindex] = float(Fraction(word))
			except ValueError: pass

	for lineindex, line in enumerate(recipe):
		for wordindex, word in enumerate(line):
			if type(word) == float and wordindex != len(line) - 1:
				if type(line[wordindex+1]) == float:
					recipe[lineindex][wordindex] += recipe[lineindex].pop(wordindex+1)

	
	for lineindex, line in enumerate(recipe):
		for wordindex, word in enumerate(line):
			if type(word) == float:
				recipe[lineindex][wordindex] = round(float(word), (2 if fuzzyMath else 5))
			for unitType in units[system]:
				for val, unit in zip(units[system][unitType].keys(), units[system][unitType].values()):
					for abbr in unit:
						if abbr == word:
							if line[wordindex-1] == 'a':
								recipe[lineindex][wordindex-1] = 1
							try:
								recipe[lineindex][wordindex-1] = numbers.index(line[wordindex-1])+1
							except ValueError: pass
							
							if line[wordindex-3] == 'a':
								recipe[lineindex][wordindex-3] = 1
							try:
								recipe[lineindex][wordindex-3] = numbers.index(line[wordindex-3])+1
							except ValueError: pass

							record = (0, abs(float(line[wordindex-1])/val * list(units[unitTo][unitType].keys())[0] - 50))
							for index, value in list(enumerate(units[unitTo][unitType].keys()))[1:]:
								score = abs(float(line[wordindex-1])/val * value - 50)
								if score < record[1]:
									record = (index, score)

							def beautify(number):
								if fuzzyMath:
									return str(round(number,2))
								else:
									return str(round(number,5))

							recipe[lineindex][wordindex] = list(units[unitTo][unitType].values())[record[0]][0]
							recipe[lineindex][wordindex - 1] = beautify(float(line[wordindex-1])/val * list(units[unitTo][unitType].keys())[record[0]])
							
							if line[wordindex-2] == 'to' and type(line[wordindex-3]) == float:
								recipe[lineindex][wordindex - 3] = beautify(line[wordindex-3]/val * list(units[unitTo][unitType].keys())[record[0]])
	
	return re.sub(r'(\d)\.0', r'\1', '\n'.join([' '.join([str(word) for word in line]) for line in recipe]))

if __name__ == '__main__':
	inp = u"""

	1.25kg/ 2.5lb potatoes (any, other than waxy potatoes, see Note 1)
	2/3 cup (160 ml) milk (full or low fat)
	3/4 cup (185 ml) thickened cream (heavy cream) (heavy cream)
	1/3 cup mayonnaise , preferably whole egg (or 1/4 cup cream) (Note 2)
	1 1/2 tsp fresh thyme leaves , plus more for garnish (or 1 tsp dried)
	2 large garlic cloves , minced
	3/4 tsp salt
	2 cups (200g) shredded cheese for mixing (Note 3)
	1 cup (100g) shredded mozzarella cheese (or sub with another cheese, Note 3)
	"""

	print(masterConvert(inp, 'us', 'metric', fuzzyMath=True))
