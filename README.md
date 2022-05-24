# Installation
1. Klona detta repo
2. Installera mysql-stöd i python

    `python3 -m pip install mysql-connector-python`

   En rekommendation är att använda en virtuell Pythonmiljö (venv)

3. Exekvera `analyze.py`
4. Resultatet skrivs ut i CSV-filer, en per test. 

# Körordning
1. Oanvända behörigheter
2. Oanvända vägval
3. Oanvända URL-er
4. Övriga oanvända objekt (TK, LA och komponenter).

# Exempel på frågor som kan analysera
## Söka fram problem i TAK
1. Logiska adresser som inte ingår i vägval och behörighet
2. Tjänstekontrakt som inte ingår i vägval och behörighet
3. Anropsbehörigheter utan matchande vägval
4. Tjänstekomponenter som inte ingår i behörighet eller utan anropsadress
5. Vägval som inte har några anropsbehörigheter
6. URL-er kopplade till tjänsteproducenter som inte används i något vägval

## Tag fram grunddata om TAK-ningar
1. Antal vägval
2. Antal anropsbehörigheter
3. Antal integrationer
4. Antal routes

# Att reda ut
## Todo
* Ändra turordning så att routings och autorizations witout - körs först
* Saknas `routing_without_a_matching_authorization`
    * Tag hänsyn till SE och * på lämpligt sätt.
* Stäm av att autorization_without_routing verkligen hanteras rätt med tanke på att vägval kan använda SE resp *. 
* Lyft fram användning av "SE" som ett fel. Även med i `summary.csv.` och med rättnings-json.
* Kolla att URL-er inte baseras på IP-adress utan på DNS-namn. 
* Skriv något om vikten av att kontrollerna sker i rätt ordning.
* När JSON-filerna implementeras ska det tydligt dokumenteras vad som måste tas bort via TAK-WEB. 
* När JSON-filerna implementeras bör det även tas fram rollback-filer.

## Done
* Lägg med information om plattform (om möjligt) i filnamnet. I alla filnamn, dvs gör tpname obligatorisk.
* ÅÄÖ blir fel i windows.
* `authoriztion_without_a_matching_routing`
    * Skall inte inkludera behörigheter som baseras på SE eller *
* Se över rubrikerna i CSV-filerna så att det blir tydligt vilken kolumn i vilken tabell de står för.
* Tag även fram sammanställning över antalet olika objekt i TAK-en. Ev tillsammans med antalet fel.
* CSV för URL-er skall även inkludera tjänstekomponent. Dock är det märkligt att samma URL kan representera olika komponenter. Kolla upp varför det blivit så. Lägg även på rubrik för tjänsteproducenten.
## deleted
Många tabeller har en kolumn vid namn *deleted*. Den verkar innehålla *null* eller *0*. Min tolkning är att *0* innebär att objektet existerar, *null* att det har tagits bort. 

# Utdata
* CSV-filer som kan läsas in i excel med listor över de problem som identifierats
* BS-JSON beställningsfiler med de rättningar som kan/bör göras av en TAK
* Tillhandahålla informationen via en webbsida (generera HTML, kanske använda Python Flask)

# Andra kontroller som skulle kunna implementeras

## Baserat på TAK
1. URL-er som inte når fram till en tjänsteproducent (går lite utanför en ren TAK-utsökning)
2. Man kan även jämföra producenters HSA-id med det cert som producenten visar upp mot RTP. Oscar har tagit fram en lista över producenter och HSA-id deras cert.

## Baserat på TAK-api
Principiellt borde alla kontroller som nu sker mot TAK-databasen kunna ske även via TAK-api. Men, eftersom man då inte skulle kunna jobba med SQL så skulle det bli betydligt mer komplicerat.

## Baserat på TPDB
1. Man skulle även kunna titta i statistiktabellen i TPDB för att lista anslutningar som inte används under en period (ex senaste året).
2. I TPDB har vi ju historik information som skulle kunna analyseras och visualiseras.
