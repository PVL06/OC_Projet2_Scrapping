![AIOHTTP Badge](https://img.shields.io/badge/AIOHTTP-2C5BB4?logo=aiohttp&logoColor=fff&style=flat) ![Beautiful soup Badge](https://shields.io/badge/BeautifulSoup-4-green)
# OC_Projet2 - Processus ETL d'un site de vente de livres

Ce projet Python implémente un processus ETL (Extract, Transform, Load) pour extraire des données à partir d'un site web de vente de livres fictif ([bookstoscrape](https://books.toscrape.com/)), les transformer et les stocker en local.

## Fonctionnalités

- Extraction de données à partir du site web de vente de livres
- Transformation des données pour assurer la cohérence et la qualité
- Chargement des données transformées dans un dossier local

## Installation

1. Cloner le repository :

```bash
git clone https://github.com/PVL06/OC_Projet2.git
cd OC_Projet2
```

2. Créer et activer un environnement virtuel Python (venv) :

```bash
python -m venv env
```
Pour activer l'environnement virtuel sur Windows, exécutez :
```bash
env\Scripts\activate
```
Sur macOS et Linux, exécutez :
```bash
source env/bin/activate
```

3. Installer les dépendances :

Utilisez pip (ou pip3 pour Python 3) pour installer les bibliothèques nécessaires :
```bash
pip install -r requirements.txt
```

## Utilisation

Exécuter le script principal pour lancer le processus ETL :
```bash
python main.py
```

## Données

A chaque lancement du programme un nouveau dossier est crée dans le dossier data qui est a la racine du projet, il a pour nom la date et l'heure de l'execution dans un format compressé.
A l'interieur se trouve un dossier par categorie qui contienne chacun un fichier csv de la categorie et un dossier contenant les images de couverture.
