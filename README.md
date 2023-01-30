# Funktion
Detta script analysera en TAK. Det finns flera sätt att presentera resultatet vilket styrs av flaggor i scriptet:

* En informationssida
* Listor i form av CSV-filer
* JSON-filer enligt formatet som Beställningsstödet använder. För vissa av analyserna skapas dessa och kan användas för att rätta TAK-en. 

Utdata är dels statistik över antal objekt av olika typ i TAKen, dels ett antal städningsunderlag. 

OBS. Modulen BsJson.py är ett bibliotek som delas mellan bs-json och analyze-tak (identiska filer används).
## Exempel på informationssida
```
venv) ➜  analyze-tak_linux git:(develop) ✗ ./analyze_tak.py -t TP_TEST -i

Denna TAK innehåller:

Antal tjänstekomponenter: 66
Antal tjänstekontrakt: 117
Antal logiska adresser: 5225
Antal anropsbehörigheter: 26025
Antal vägval: 31826
Antal URL-er: 203

Följande märkligheter har identifierats i denna TAK (städning skall ske i samma ordning som listas nedan):

Anropsbehörigheter till icke existerande vägval: 1692
Vägval som saknar anropsbehörigheter: 16
Logiska adresser som inte förekommer i något vägval: 349
Tjänstekontrakt som inte förekommer i någon anropsbehörighet: 56
Tjänstekontrakt som inte förekommer i något vägval: 43
Tjänstekomponenter som inte förekommer i något vägval eller någon anropsbehörighet: 11
Behörigheter baserade på logisk adress "SE" (bör ändras till "*"): 13
Vägval baserade på logisk adress "SE" (bör ändras till "*"): 11
URL-er som inte används i något vägval: 37
URL-er som specificerar IP-adresser istället för DNS-namn: 0

Informationen ovan har skrivits ut till summary.TP_TEST.csv
```

## Städning av TAK
Baserat på informationen som scriptet genererar kan en TAK städas från felaktig och död information. Städningen skall ske i den ordning som visas i informationssidan ovan. Det måste ske iterativt - efter varje städning skall scriptet exekveras på nytt och det uppdaterade underlagen användas för nästa steg. 

# Installation
1. Klona detta repo
2. Sätt upp pythonmiljön. Det är ofta en god idé att använda en virtuell miljö:
    ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install mysql-connector-python
   ```
3. Scriptet behöver tillgång till en exekverande mysql/mariadb TAK-databas. En användare med enbart läsrättigheter rekommenderas starkt! 
4. Exekvera `analyze_tak.py`. Information om nödvändiga flaggor skrivs ut.
 

# Möjliga förbättringar

* Lägg till information om antal standardbehörigheter och -vägval
* Ändra benämning av "URL" till "Anropsadress"! En anropsadress består av en url och en tjänstekomponentsreferens.
* När JSON-filerna implementeras bör det ev tas fram rollback-filer.
* Överväg att lägga på en kontroll över att namnrymderna är korrekta.
* Lista konsumenter som har både explicit och standardbehörighet till ett vägval.
* Lista konsumenter som enbart har explicita behörigheter till standardvägval.


## Genomfört
* Skriv en dokumentation i denna readme.
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

# Att begrunda
## deleted
Se [https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning](https://skl-tp.atlassian.net/wiki/spaces/SKLTP/pages/2344353793/SKLTP+TAK+-+Beskrivning+av+implementation+f+r+borttagning)

Min tolknig av texten är att om deleted-flaggan är NULL så
indikerar det att posten är borttagen. Alla andra värden står för "FALSE", dvs att posten inte är deleted. Det gör att kontrollen "IS NOT NULL" visar att en post existerar.

Förutom kolumnen deleted behöver även tomDatum kontrolleras. Om det är "före" aktuellt datum måste också posten betraktas som deleted.


## Andra kontroller som skulle kunna implementeras

### Baserat på TAK
1. URL-er som inte når fram till en tjänsteproducent (går lite utanför en ren TAK-utsökning)
2. Man kan även jämföra producenters HSA-id med det cert som producenten visar upp mot RTP. Oscar har tagit fram en lista över producenter och HSA-id deras cert.

### Baserat på TAK-api
Principiellt borde alla kontroller som nu sker mot TAK-databasen kunna ske även via TAK-api. Men, eftersom man då inte skulle kunna jobba med SQL så skulle det bli betydligt mer komplicerat.

### Baserat på TPDB
1. Man skulle även kunna titta i statistiktabellen i TPDB för att lista anslutningar som inte används under en period (ex senaste året).
2. I TPDB har vi ju historik information som skulle kunna analyseras och visualiseras.
