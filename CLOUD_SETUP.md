# Cloud-Anbindung & automatischer PDF-Build

So werden die PDFs **automatisch bei jedem Push** gebaut und in die Cloud
(Infomaniak kDrive) geladen — und von dort per Link für die Eigentümer:innen
freigegeben.

```
 git push  ──▶  GitHub Actions  ──▶  baut NUR geänderte .md zu PDF/DOCX
                                 └─▶  rclone-Upload nach Infomaniak kDrive
                                                         └─▶  Freigabe-Link für Eigentümer
```

- Quelle der Wahrheit bleibt das Git-Repo (Markdown).
- Unveränderte PDFs werden **weder neu gebaut noch erneut hochgeladen**.
- Workflow: [.github/workflows/build-and-publish.yml](.github/workflows/build-and-publish.yml)

---

## Einmalige Einrichtung

### 1. Infomaniak kDrive anlegen (kostenlos)

1. Auf <https://www.infomaniak.com/de/ksuite/kdrive> ein **kostenloses kDrive**
   (15 GB) erstellen.
2. Empfehlung: **Zwei-Faktor-Authentifizierung** im Infomaniak-Manager aktivieren.

### 2. WebDAV-Zugangsdaten holen

1. Im kDrive bzw. Infomaniak-Manager den **WebDAV-Zugang** aktivieren.
   Du erhältst eine URL der Form
   `https://<kennung>.connect.kdrive.infomaniak.com/<kennung>`.
2. **Benutzername:** deine Infomaniak-E-Mail.
3. **Passwort:** im Manager unter *Sicherheit* ein **Anwendungs-Passwort**
   erstellen (nicht das Hauptpasswort verwenden — nötig bei aktivierter 2FA).

### 3. GitHub-Secrets hinterlegen

Im Repo: **Settings → Secrets and variables → Actions → New repository secret**
folgende drei Secrets anlegen:

| Name | Wert |
|---|---|
| `KDRIVE_WEBDAV_URL` | die WebDAV-URL aus Schritt 2 |
| `KDRIVE_USER` | deine Infomaniak-E-Mail |
| `KDRIVE_PASS` | das Anwendungs-Passwort |

Optional als **Variable** (Tab „Variables"): `KDRIVE_DEST` = Zielordner im
kDrive (Standard: `Hausverwaltung/Export`).

> Solange diese Secrets fehlen, baut der Workflow die PDFs trotzdem — er
> überspringt nur den Upload (kein Fehler).

### 4. Testen

- **Actions → „PDFs bauen & in die Cloud pushen" → Run workflow** (manuell),
  Option *rebuild_all* = true für einen ersten Komplettlauf.
- Danach erscheinen die PDFs im kDrive unter `Hausverwaltung/Export/…`.

### 5. Für Eigentümer freigeben

Im kDrive-Web den Ordner `Hausverwaltung/Export` (oder einen Unterordner mit nur
den freizugebenden Protokollen) per **Freigabe-Link** teilen — optional mit
**Passwort** und **Ablaufdatum**. Diesen Link an die Eigentümer:innen schicken;
sie brauchen kein eigenes Konto.

> Tipp: Lege im kDrive z. B. einen Ordner `Eigentümer/` an und teile nur diesen.
> Sensible interne Dokumente (z. B. `Fenstertausch_Seria/`) dann **nicht**
> in den freigegebenen Ordner spiegeln.

---

## Optional: lokal manuell hochladen

```bash
rclone config create kdrive webdav \
  url="https://<kennung>.connect.kdrive.infomaniak.com/<kennung>" \
  vendor=other user="deine@email" pass="$(rclone obscure 'ANWENDUNGS_PASSWORT')"
./build.sh                      # PDFs bauen (inkrementell)
rclone copy Export kdrive:Hausverwaltung/Export -v
```

---

## Hinweise

- **GitHub Actions** ist für private Repos inkl. Freikontingent (ca. 2.000
  Min./Monat) nutzbar; ein Lauf dauert nur wenige Minuten.
- **App-Server später:** geplant auf **Oracle Cloud Always Free** (ARM/Ampere,
  bis 4 Kerne + 24 GB RAM gratis). Sensible Daten bleiben in der EU/CH
  (Infomaniak); Oracle nur als Compute, idealerweise EU-Region (Frankfurt/Zürich).
