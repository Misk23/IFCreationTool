# IFCreationTool

creationTool.tx - textX fajl koji sluzi za opis sveta, metamodel za opis objekata, sekcija i igraca

game.tx - textX fajl koji sluzi za opis komandi igrice, metamodel za opis komandi (go, look, take, drop...)

program.ct - ovde koristimo creatonTool.tx gramatiku za opis konkretnog sveta i modela

example.game - ovde koristimo game.tx gramatiku za opis jednog playthrough-a

main.py - python fajl koji sadrzi klasu Game, koja sa svojom build metodom parsira konkretan model opisan sa creationTool.tx i mapira ga na odgovarajuce python klase(class Section, class Object...)
dok svojom play methodom interpretira komande konkretnog playthrough-a opisanog sa game.tx
