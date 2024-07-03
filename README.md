# OC_Projet2

## Projet 2 de la formation OpenClassRooms developpeur Python

### Présentation
Le but est d'automatiser la récupération des données du site "Books to Scrape", fake site de vente en ligne de livre, via un programme de scrapping.
A chaque exéctution du programme les données sont stockées dans un dossier "data/id" ou id représente la date et l'heure au format compressé lors du lancement.
A l'interieur se trouve un dossier pour chaque catégorie qui contient un fichier csv et un dossier contenant toute les images de couverture au format jpg.
Les fichiers csv utilise la virgule comme séparateur et l'entête ce compose comme suit:
    ● universal_ product_code
    ● title
    ● price_including_tax
    ● price_excluding_tax
    ● number_available
    ● product_description
    ● category
    ● review_rating
    ● image_url

### Prérequis

Python > 3.10, pip

### Exécution

```
python -m venv .venv
source .venv/Scripts/activate # for linux os
./.venv/Scripts/activate      # for windows os
pip install -r requirements.txt
python main.py
```
