# Installation
1. Klona detta repo
2. Sätt upp pythonmiljön
    ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install mysql-connector-python
   ```
3. Exekvera `analyze_tak.py`. Information om nödvändiga flaggor skrivs ut.
4. Resultatet skrivs ut i CSV-filer, en per test. 

# Körordning
1. Oanvända behörigheter
2. Oanvända vägval
3. Standarvägval utan standardbehörighet
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
7. Verifiera att HSA-id för tjänstekomponenter enbart innehåller legala karaktärer (inte ex underscore).

## Tag fram grunddata om TAK-ningar 
1. Antal vägval
2. Antal anropsbehörigheter
3. Antal integrationer
4. Antal routes

# Att reda ut
## Todo
* Addera kontroll av att alla standardvägval motsvaras av standardbehörighet.
* Ändra benämning av "URL" till "Anropsadess"! En anropsadress består av en url och en tjänstekomponentsreferens.
* Uppenbarliigen är logiken kring delete-kolumen mer komplex (rörig/felaktig) än vad jag initialt trodde. Kontrollen för "deleted" behöver byggas ut. Se [https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning](https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning)
* När JSON-filerna implementeras bör det ev tas fram rollback-filer.
* Skriv en dokumentation i denna readme.
* Överväg att lägga på en kontroll över att namnrymderna är korrekta.

## Done
* Skriv något om vikten av att kontrollerna sker i rätt ordning.
* Kolla att URL-er inte baseras på IP-adress utan på DNS-namn.
* Ändra turordning så att routings och authorizations without - körs först
* Stäm av att autorization_without_routing verkligen hanteras rätt med tanke på att vägval kan använda SE resp *.
* Lyft fram användning av "SE" som ett fel. Även med i `summary.csv.` och med rättnings-json.
* Saknas `routing_without_a_matching_authorization`
* Lägg med information om plattform (om möjligt) i filnamnet. I alla filnamn, dvs gör tpname obligatorisk.
* ÅÄÖ blir fel i windows.
* `authoriztion_without_a_matching_routing`
    * Skall inte inkludera behörigheter som baseras på SE eller *
* Se över rubrikerna i CSV-filerna så att det blir tydligt vilken kolumn i vilken tabell de står för.
* Tag även fram sammanställning över antalet olika objekt i TAK-en. Ev tillsammans med antalet fel.
* CSV för URL-er skall även inkludera tjänstekomponent. Dock är det märkligt att samma URL kan representera olika komponenter. Kolla upp varför det blivit så. Lägg även på rubrik för tjänsteproducenten.
## deleted
Uppenbarliigen är logiken kring delete-kolumen mer komplex (rörig/felaktig) än vad jag initialt trodde. Kontrollen för "deleted" behöver byggas ut. Se [https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning](https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning)

Min tolknig av texten är att om deleted-flaggan är NULL så
indikerar det att posten är borttagen. Alla andra värden står för "FALSE", dvs att posten inte är deleted. Det gör att kontrollen "IS NOT NULL" visar att en post existerar.

Förutom kolumnen deleted behöver även tomDatum kontrolleras. Om det är "före" aktuellt datum måste också posten betraktas som deleted.



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
