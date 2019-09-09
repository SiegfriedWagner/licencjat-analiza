# TODO: Cleanup and documentation
import itertools as it
import random
random.seed(2019)


# Film panel permutations
films_panel_permuts = [("", "Przewiń listę filmów dwa razy w dół. ", "Przewiń listę filmów do góry. "), 
              ("Przewiń listę filmów dwa razy w dół. ", "", "Przewiń listę filmów do góry. "), 
              ("Przewiń listę filmów dwa razy w dół. ", "Przewiń listę filmów do góry. ", "")]
# Film number task permutations
films_number_permuts = list(it.permutations(range(1,5), 3))
# Volume task permutations
volumes_permut = [(25, 50, 75), (75, 50, 25)]
# Generate film wind permutations
loops = list(it.permutations([25, 50, 75]))
back = list(it.permutations([0, 0, 1]))
wind_permuts = []  

print(loops)
print(back)
for wind, b in it.product(loops, [1,2,3]): # Negative value represents rewinding by 25%
    print(wind, b)
    _ = list(wind)
    _.insert(b, -wind[b-1])
    wind_permuts.append(_)

# Optional print all sets of permutations
'''
print(wind_permuts)
print(volumes_permut)
print(films_panel_permuts)
print(films_number_permuts)
'''
# for element in it.product(wind_permuts, volumes_permut, films_panel_permuts, films_number_permuts):
#     print(element)

docelowe_kombinacje = list(it.product(wind_permuts, volumes_permut, films_number_permuts, films_panel_permuts))
def gen_przewin(idx, lista):
    if lista[idx] < 0:
        return ""
    else:
        ret = f"\nPrzewiń film do {lista[idx]}%"
        try:
            if lista[idx+1] < 0:
                ret += f"\nPrzewiń film do {lista[idx]-25}%"
        except:
            pass
        return ret

ile = 120
l = 0
co_ktory = len(docelowe_kombinacje)//ile
# Number of all task sets
print(len(docelowe_kombinacje))
first, second, third = [], [], [] # task type buckets
# Cyclic list contatining task buckets
cycle = it.cycle([first, second, third]) 
# Create file with chosen tasks for experiment. Splits tasks into buckets.
with open('all_combinations', 'w', encoding="utf-8") as out_file:
    for przewijanie, glosnosc, film, panel in docelowe_kombinacje:
        current = 1
        out = f"""
{gen_przewin(0, przewijanie)}
Ustaw głośności na {glosnosc[0]}%
Wstrzymaj, a następnie wznów film.
{panel[0]}Wybierz {film[0]} film z listy.{gen_przewin(1, przewijanie)}
Wstrzymaj, a następnie wznów film.
Ustaw głośność na {glosnosc[1]}%
{panel[1]}Wybierz {film[1]} film z listy.{gen_przewin(2, przewijanie)}
Ustaw głośność na {glosnosc[2]}%
Wstrzymaj, a następnie wznów film.
{panel[2]}Wybierz {film[2]} film z listy.{gen_przewin(3, przewijanie)}
Zatrzymaj film."""
        if l % co_ktory == 0:
            next(cycle).append(out) # Saves tasks to appropriate buckets
            out_file.write(out)
        l+=1

random.shuffle(first)
random.shuffle(second)
random.shuffle(third)

for tup in zip(first, second, third):
    print(tup[0])
    print(tup[1])
    print(tup[2])

# import glob
# subjects = glob.glob("./data_temp/*")
# for subject, tasks in zip(subjects, zip(first, second, third)):
#     interfaces = glob.glob(subject + "/*")
#     for interface, task in zip(interfaces, tasks):
#         with open(interface + "/task.txt", 'w') as file:
#             file.write(task.strip())
