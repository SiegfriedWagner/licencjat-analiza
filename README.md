# Opis zawartości

## Analiza

Przed wykonaniem analizy upewnij się, że masz zainstalowanego Pythona 3 oraz język R, a także zainstaluj niezbednę pakiety wyszczególnione w **requirements.txt**.

    pip install -r requirements.txt --user

**analiza.ipynb** - [Jupyter Notebook](https://jupyter.org/) zawierający całą analizę danych



## Dane

**sus.csv** - wyniki ankiety SUS

**szerego.csv** - wyniki ankiety końcowej

**testy_poznawcze.csv** - wyniki testów poznawczych

**time_series.csv** - pogrupowane dane z zadań

**osobowe.csv** - wybrane cechy badanych

**eyetracking_events** - folder z danymi o zdarzeniach na podstawie rejestracji okulografu

## Pliki języka Python

**csv_operations/csv_parser.py** - parser surowych logów do postaci widocznej w **time_series.csv**

**csv_operations/csv_validator.py** - walidator zawracający pliki do ręcznej korekcji przed przetworzeniem przez **csv_parser.py**

**helpers.py** - fukcje używane w m.in. w analizie

**task_order.py** - generator kolejności testowania interfejsów dla badanych

**task_generator.py** - generator kolejności zadań dla dla badanych