<!--
CE DOCUMENT N'A PAS VOCATION A ÊTRE LU DIRECTEMENT OU VIA GITHUB :
les liens seront cassés, l'affichage ne sera pas correcte. Ne faites ça !

Consultez la doc en ligne ici : https://geoplateforme.github.io/sdk-entrepot/

Le lien vers cette page devrait être : https://geoplateforme.github.io/sdk-entrepot/tutoriel_pcrs/
-->

# Tutoriel : publier un flux PCRS

La Géoplateforme permet d'héberger et diffuser vos données PCRS raster/image (Plan Corps de Rue Simplifié).

Pour cela, vous devez téléverser des dalles « PCRS » qui permettront de créer une pyramide image qui sera diffusée en flux.

Voici les prérequis pour suivre ce tutoriel :

* vous devez disposer d'un compte Géoplateforme (création en suivant ce [tuto](https://geoplateforme.github.io/tutoriels/production/controle-des-acces/entrepot/creation_compte/) ou sur [cartes.gouv](https://cartes.gouv.fr/))
* vous devez disposer d'un datastore (pour sa création, vous pouvez contacter geoplateforme@ign.fr ou faire une demande [ici](https://cartes.gouv.fr/entrepot/demande-de-creation) en précisant votre établissement, qu'il s'agit d'une diffusion partenaire PCRS et votre identifiant utilisateur que vous trouver sur votre [espace](https://cartes.gouv.fr/mon-compte))
* vous devez avoir installé python et le module [SDK](index.md)

Vous allez avoir besoin de 3 fichiers pour réaliser le tutoriel dont le contenu va être détaillé :

* un fichier de configuration pour définir vos paramètres SDK
* un fichier descripteur qui détaille votre livraison
* un fichier de workflow en plusieurs étapes qui effectuera les traitements

## Définition de la configuration

Vous allez devoir déposer à la racine du dossier de votre projet un fichier `config.ini` contenant les informations suivantes :

```text
# Informations pour l'authentification
[store_authentification]
# paramètres du SDK
client_id=gpf-warehouse
client_secret=BK2G7Vvkn7UDc8cV7edbCnHdYminWVw2
# Votre login
login=********
# Votre mot de passe
password=********

# Informations pour l'API
[store_api]
# L'identifiant de votre datastore
datastore=********
```

Il faut compléter le fichier avec votre login/mot de passe et l'identifiant du datastore qui vous a été aloué.

Vous pouvez tester la validité de votre fichier avec la commande suivante :

```text
python3 -m sdk_entrepot_gpf me
```

Cela devrait renvoyer :

```text
Vos informations :
  * email : ********
  * nom : ********
  * votre id : ********

Vous êtes membre de 1 communauté(s) :

  * communauté « ******** » :
      - id de la communauté : ********
      - id du datastore : ********
      - nom technique : ********
      - droits : community, uploads, processings, datastore, stored_data, broadcast
```

Il peut être nécessaire de rajouter certains paramètres pour que cela fonctionne comme le proxy si vous en utilisez un. Vous pouvez suivre la page [configuration](configuration.md) pour compléter votre fichier si nécessaire.

## Fichier descripteur de livraison

Vous allez devoir créer un fichier `PCRS_descriptor.jsonc` à la racine de votre projet avec les informations suivantes :

```text
{
    "datasets": [
        {
            "data_dirs": [
                "$votre_chantier_PCRS"
            ],
            "upload_infos": {
                "description": "Description de votre chantier (département, zone, date...)",
                "name": "$votre_chantier_PCRS",
                "srs": "EPSG:2154",
                "type": "RASTER"
            },
            "comments": [
                "Votre commentaire"
            ],
            "tags": {
                "datasheet_name": "$votre_chantier_PCRS",
                "type": "PCRS"
            }
        }
    ]
}
```

Il faut remplacer 3 fois dans le fichier `$votre_chantier_PCRS` par une valeur sous la forme `PCRS_chantier_********` (ex: PCRS_chantier_D046). Cette valeur vous permettra de retrouver votre fiche de données sur cartes.gouv.fr. Vous pouvez également compléter le fichier avec une description et éventuellement un commentaire.

***ATTENTION** Si vous utilisez le jeu de données test pour l'expérimentation, la valeur `$votre_chantier_PCRS` est également utilisée pour définir le nom des couches. Comme il y a unicité de nom pour les couches sur les services publics, nous vous encourageons à enrichir cette valeur pour qu'elle soit différente d'un testeur à l'autre (ex: PCRS_chantier_D046_test_PACA).*

Vous déposerez vos données dans un répertoire du même nom `$votre_chantier_PCRS` à la racine de votre projet comme suit :

```text
$votre_chantier_PCRS/
├── dalle_1.tif
├── dalle_2.tif
└── ...
```

Vous pouvez maintenant effectuer la livraison en lançant la commande depuis la racine de votre projet ou en indiquant le chemin du fichier descripteur au programme :

```sh
python3 -m sdk_entrepot_gpf delivery PCRS_descriptor.jsonc
```

Le programme doit vous indiquer que le transfert est en cours, puis qu'il attend la fin des vérification côté API avant de conclure que tout est bon `INFO - BILAN : les 1 livraisons se sont bien passées` (cela peut être long selon la taille de la livraison et la qualité de votre connexion, ne fermez pas votre terminal pendant ce temps).

Si votre connexion est interrompue, vous pouver reprendre la livraison avec la commande :

```sh
python3 -m sdk_entrepot_gpf delivery PCRS_descriptor.jsonc -b CONTINUE
```
 
Il y a deux vérifications effectuées sur la livraison :

* la vérification standard qui s'assure que les données ne sont pas corrompues lors du transfert
* la vérification raster qui s'assure que les données sont valides

Si une des deux vérification échoue, vous pourrez obtenir les logs d'erreur détaillés en indiquant l'id de votre livraison dans la commande :

```sh
python3 -m sdk_entrepot_gpf upload ******** --checks
```

## Workflow

Une fois les données livrées, il faut créer la pyramide image avant de la diffuser en flux (WMSRaster et WMTS).

Ces étapes sont décrites grâces à un workflow.

Vous pouvez récupérer le template du workflow grâce à la commande suivante :

```sh
python3 -m sdk_entrepot_gpf example workflow PCRS.jsonc
```

Pour plus de détails, consultez la [documentation sur les workflows](workflow.md).

Le workflow `PCRS.jsonc` est composé de 2 étapes (une pour la génération de la pyramide et une pour la publication des flux). Il faudra lancer une commande pour chacune d'elles.

Les commandes à lancer sont les suivantes :

```sh
# partie génération de la pyramide
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s pyramide --param producteur $votre_chantier_PCRS
# partie publication
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s publication --param producteur $votre_chantier_PCRS
```

La première commande peut être longue selon le nombre de dalles livrées. Des logs doivent vous être remontés et se terminer par :

```text
INFO - Exécution de l'action 'pyramide-0' : terminée
```

Avec la deuxième commande, deux offres (une WMTS et une WMSRaster) devraient être créées :

```text
INFO - Offre créée : Offering(id=********, layer_name=$votre_chantier_PCRS)
```

Vous pouvez maintenant retrouver vos données dans cartes.gouv (https://cartes.gouv.fr/entrepot/$id_datastore/donnees/$votre_chantier_PCRS) ou les visionner dans un SIG comme QGIS en renseignant les urls des GetCapabilities des services ([WMTS](https://data.geopf.fr/wmts?service=WMTS&request=GetCapabilities) et [WMSRaster](https://data.geopf.fr/wms-r?)).

## Suppression de la livraison

Afin de ne pas surcharger l'espace de livraison et de ne pas atteindre vos quotas lors de livraisons ultérieures, une fois que vous avez validez vos flux, vous pouvez supprimer la livraison avec la commande suivante :

```sh
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s upload_delete --param producteur $votre_chantier_PCRS
```

Le programme doit vous indiquer que la suppression s'est bien passée `INFO - Suppression effectuée.`.

## Nettoyage de fin d'expérimentation

Dans le cadre de l'utilisation du jeu de données test pour l'expérimentation, vous pouvez dépublier vos couches et supprimer la pyramide avec la commande suivante :

```sh
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s depublication --param producteur $votre_chantier_PCRS
```

Le programme va vous demander de confirmer les entités à supprimer `INFO - Voulez-vous effectuer la suppression ? (oui/NON)`, vous allez devoir répondre `oui` si les entités listées en vert au-dessus correspondent bien à celles à supprimer.

## Mise à jour

Si une mise à jour concerne l'ensemble du territoire d'une APLC (Autorité Publique Locale Compétente), nous préconisons de construire une nouvelle pyramide et de diffuser des nouvelles offres en reprenant le [tutoriel](tutoriel_pcrs.md) du début.

Si une mise à jour ne concerne qu'une emprise limitée, vous allez pouvoir créer une nouvelle pyramide qui prendra en compte les nouvelles dalles et mettre à jour les offres.

Pour cela, livrez les nouvelles dalles en ajoutant un tag version à votre fichier descripteur.

```text
{
    "datasets": [
        {
            "data_dirs": [
                "$votre_chantier_PCRS_v2"
            ],
            "upload_infos": {
                "description": "Description de votre chantier (département, zone, date...) maj v2",
                "name": "$votre_chantier_PCRS_v2",
                "srs": "EPSG:2154",
                "type": "RASTER"
            },
            "comments": [
                "Votre commentaire"
            ],
            "tags": {
                "datasheet_name": "$votre_chantier_PCRS",
                "type": "PCRS",
                "version": "2"
            }
        }
    ]
}
```

```sh
python3 -m sdk_entrepot_gpf delivery PCRS_descriptor_maj.jsonc
```

Puis, générez la nouvelle pyramide avec la commande suivante (laissez le paramètre `old_version` vide si il s'agit d'une mise à jour de la pyramide initiale) :

```sh
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s pyramide_maj --param producteur $votre_chantier_PCRS --param old_version "" --param new_version 2
```

Si il s'agit d'une mise à jour itérative, renseignez le paramètre `old_version` :

```sh
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s pyramide_maj --param producteur $votre_chantier_PCRS --param old_version 2 --param new_version 3
```

Vous pouvez ensuite mettre à jour les offres avec la commande :

```sh
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s publication_maj --param producteur $votre_chantier_PCRS --param old_version "" --param new_version 2
```

Une fois que vous avez validé les nouvelles offres, vous pouvez si vous souhaitez faire de l'historisation pour comparer (attention aux quotas de votre datastore).

```sh
# Si vous souhaitez publier l'ancienne pyramide
python3 -m sdk_entrepot_gpf workflow -f PCRS.jsonc -s publication_old --param producteur $votre_chantier_PCRS --param old_version ""
```
