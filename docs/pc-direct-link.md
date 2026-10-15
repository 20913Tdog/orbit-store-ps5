# Download am PC freigeben, auf der PS5 laden

Experimenteller Eigenbau auf Basis des offiziellen Orbit-Store-Quellpakets **1.3.5**.
Entwicklungsbranch: [`feat/pc-direct-link`](https://github.com/20913Tdog/orbit-store-ps5/tree/feat/pc-direct-link).
Angezeigte Service-Version: **1.3.6-beta.1** (eigener Testbuild auf Basis von 1.3.5).
Die Beta-Nummer sorgt dafür, dass die offizielle 1.3.5-TV-App beim Neustart die gespeicherte PC-Link-Version auswählt.
Die native TV-App wurde nicht verändert. Für die neuen nativen Bedienelemente und den verbesserten Dialogablauf die offizielle **1.3.5-TV-App** verwenden:
[PPSA99177.ffpkg](https://github.com/saawant12/orbit-store-ps5/releases/download/v1.3.5/PPSA99177.ffpkg).
Danach unseren Dienst über die neue `orbit_store.elf` starten. Orbit Zero wird für die PC-Link-Funktion nicht benötigt.
Die offiziellen Orbit-Zero-1.3.5-Pakete können unabhängig davon verwendet werden.

## Testbuild starten

1. Deine bisherige Orbit-ELF aufbewahren. Für eine vollständige Rückkehr zusätzlich
   `/data/orbit-store/` und den bestehenden Orbit-Eintrag im Payload Manager sichern.
2. Laufende Downloads pausieren. In Orbit **App-Einstellungen → Update / neu installieren →
   Orbit zum Neustart stoppen** wählen und warten, bis der Dienst beendet ist.
3. Die mitgelieferte `orbit_store.elf` über deinen vorhandenen Payload Manager oder
   ELF Loader starten. Am PC `http://<PS5-IP>:34177/` öffnen, neu laden und bei Bedarf koppeln.
   Unter App-Einstellungen sollte **1.3.6-beta.1** stehen.

Orbit speichert beim Start wie gewohnt eine Laufzeitkopie unter
`/data/orbit-store/orbit_store.elf` und aktualisiert bereits von Orbit verwaltete
Manager-Kopien. Der Test ist deshalb nicht auf die laufende Sitzung beschränkt.
Zur vollständigen Rückkehr Orbit stoppen und die gesicherten Dateien einschließlich
`saved-version.txt` und des verwalteten Manager-Eintrags wiederherstellen.

## Download übergeben

1. Im **PC-Browser** die Orbit-Seite öffnen, Spiel, Quelle und Ziellaufwerk wählen.
   Der Bereich **„Download-Link vom Computer verwenden“** ist immer geöffnet.
2. **„Sourcefile öffnen“** wählen. Im neuen Tab die normalen
   Anbieter-Schritte abschließen. Deinen Popup-Blocker kannst du dabei eingeschaltet lassen;
   Orbit öffnet den angeforderten Tab direkt aus deinem Klick.
3. Die endgültige **Datei-URL** in **„Direkter Download-Link“** einfügen und
   **„Auf PS5 herunterladen“** wählen. Die PS5 prüft die Datei und lädt sie auf
   das ausgewählte Laufwerk. Den Fortschritt zeigt Orbit unter Downloads.

Ohne eingefügten Link öffnet **„Auf PS5 herunterladen“** die Anbieterseite wie bisher auf der PS5.
Die neuen Bedienelemente erscheinen nur im PC-Browser; auf der PS5 bleibt der bisherige Ablauf erhalten.

Bei Vikingfile ist die Datei-URL eine Adresse wie
`https://vikingfile.com/d/<Token>/<Dateiname>`. Die Seite mit `/f/` ist noch kein Download-Link.
Du kannst den fertigen Link aus dem Download-Eintrag deines Browsers kopieren.
Falls der Browser ihn dort nicht anbietet: Entwicklerwerkzeuge → Netzwerk öffnen,
Protokoll beibehalten, den Download auslösen und die URL der tatsächlichen Datei-Anfrage kopieren.
Einen versehentlich begonnenen PC-Download anschließend abbrechen.

Das Feld nennt den erwarteten Dateinamen. Eine andere Datei, eine HTML-Seite oder
eine abweichende Dateigröße wird abgelehnt. Es werden keine Browser-Cookies an Orbit übertragen.

## Was geprüft wurde

- Web-Build, TypeScript und alle zehn Übersetzungskataloge.
- Fünfzehn Tests des echten Backend-Workers mit der produktiven Anbieter-Allowlist:
  gültiger Link, falscher Host/Dateiname/Datentyp, Abbruch, parallele Anfrage,
  Quellen- und Katalogänderung, Link-Erneuerung eines pausierten Jobs sowie native Dialogbestätigung und beide Rückkehrziele aus 1.3.5.
- Vierzehn Browser-Szenarien: alle vier Oberflächen, blockierter Tab, API-Fehler,
  unzulässige Seitenadresse, abgelehnter Datei-Link, leeres Feld sowie PS5-Erkennung über lokale Sitzung und Browserkennung.
- HTTP-Integration mit dem vollständigen Testdienst und Archive.org-An-/Abmeldung gegen lokale Testdaten: Kopplung, Herkunftsprüfung,
  Dateiname, Größe, Dateityp, stabile Datei-Identität, Byte-Probe und vollständiger
  Download mit Prüfsumme in ein temporäres Laufwerk.
- Neustart-Auswahl gegen den unveränderten Starter der offiziellen 1.3.5-TV-App.
- PS5-Payload mit SDK 0.43 aus den festgelegten Bibliotheksquellen gebaut.

**Praxistest:** Die PC-Funktion im vorherigen Build 1.3.1-beta.2 wurde auf der echten PS5 bestätigt. Die neue Kombination mit 1.3.5 muss noch auf der Konsole getestet werden. PC und PS5 sollten dafür zunächst dasselbe Heimnetz und denselben
Internetzugang verwenden. Ob der Anbieter zusätzlich Cookies oder eine bestimmte
Browser-Sitzung voraussetzt, entscheidet dieser Praxistest.

Diese erste Version verlangt das Einfügen des fertigen Links. Die automatische
Übernahme per Browser-Erweiterung ist ein möglicher nächster Schritt.

## Entwicklung

Der ursprüngliche öffentliche GitHub-Hauptbranch enthält Dokumentation und Releases.
`backend/`, `src/`, `app/` und Build-Werkzeuge stammen aus dem offiziellen
`orbit-store-1.3.5-source.tar.gz` im Release-Quellpaket. Der Änderungs-Patch bezieht
sich auf diesen Quellstand; die vollständige Arbeitskopie enthält ihn bereits.
In diesem Fork liegt die Entwicklung auf `feat/pc-direct-link`. Der Import des
offiziellen Quellstands und die Erweiterung sind in getrennten Commits abgelegt.

Neue Schnittstellen:

- `GET /api/v1/browser/page?releaseId=…`: liefert nach Kopplung und Prüfung der
  aktivierten Quelle die zum Katalogeintrag gehörende Anbieterseite.
- `POST /api/v1/browser` mit `action: "start"` oder `"refresh"` akzeptiert optional
  `directUrl`. Ohne dieses Feld bleibt der bisherige PS5-Browserablauf erhalten.
  Mit dem Feld folgen dieselben Datei- und Queue-Prüfungen ohne Browser-Capture.

Der Link wird weder in Navigationsparametern noch im Browser-Status zurückgegeben.
Bestehende Abbruch-, Quellen-, Speicher- und Dateiprüfungen bleiben wirksam.

Gezielte Tests nach Einrichtung der Build-Umgebung aus `BUILDING.md`:

```sh
npm ci
npm run typecheck
npm test
make test-pc-link
```

Für die Browser-Tests zusätzlich Playwright in der Entwicklungsumgebung installieren
(nicht auf der PS5 und nicht für normale Anwender erforderlich):

```sh
npm install --no-save --package-lock=false playwright
npx playwright install chromium --only-shell
npm run test:pc-link:ui
```

Die Browser-Tests starten nur einen lokalen Testserver und ersetzen alle Anbieter-
und PS5-Anfragen durch Testdaten. Sie öffnen keinen Browser auf deinem Computer.
