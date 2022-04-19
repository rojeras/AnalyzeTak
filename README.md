# Installation
1. Klona detta repo
2. Installera mysql-stöd i python

    `python3 -m pip install mysql-connector-python`

   En rekommendation är att använda en virtuell Pythonmiljö (venv)

3. Exekvera `analyze.py`
4. Resultatet skrivs ut i CSV-filer, en per test. 
# Exempel på frågor som kan analysera
## Söka fram problem i TAK
1. Logiska adresser som inte ingår i vägval och behörighet
2. Tjänstekontrakt som inte ingår i vägval och behörighet
3. Anropsbehörigheter utan matchande vägval
4. Tjänstekomponenter som inte ingår i behörighet eller utan anropsadress
5. Vägval som inte har några anropsbehörigheter
6. URL-er kopplade till tjänsteproducenter som inte används i något vägval
7. URL-er som inte når fram till en tjänsteproducent (går lite utanför en ren TAK-utsökning)
8. Man kan även jämföra producenters HSA-id med det cert som producenten visar upp mot RTP. Oscar har tagit fram en lista över producenter och HSA-id deras cert. 
9. Man skulle även kunna titta i statistiktabellen i TPDB för att lista anslutningar som inte används under en periuod (ex senaste året).

## Tag fram grunddata om TAK-ningar
1. Antal vägval
2. Antal anropsbehörigheter
3. Antal integrationer
4. Antal routes

# Att reda ut
## deleted
Många tabeller har en kolumn vid namn *deleted*. Den verkar innehålla *null* eller *0*. Min tolkning är att *0* innebär att objektet existerar, *null* att det har tagits bort. 
