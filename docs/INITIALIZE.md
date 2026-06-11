[Documentation index](./index.md)

# dnsforge initialize

`dnsforge initialize` prend en main la configuration locale d'un BIND déjà installé par le composant `install/`.

La commande ne fait **aucune installation de paquet système**. Elle ne remplace pas l'installateur.

## Responsabilité

`initialize` exécute uniquement le cycle de déploiement BIND DNSForge :

1. lecture de `/etc/dnsforge/setup.conf`, source de vérité du nœud ;
2. rendu des templates DNSForge ;
3. contrôle des prérequis BIND (`named-checkconf`, `rndc`, `systemctl`) ;
4. sauvegarde complète de la configuration BIND existante par déplacement puis archive `tar.gz` ;
5. déploiement des nouveaux fichiers BIND générés ;
6. validation `named-checkconf` ;
7. restauration des contextes SELinux si applicable ;
8. `systemctl daemon-reload` ;
9. activation et redémarrage de `named` ;
10. verrouillage définitif de l'initialisation dans un fichier technique masqué.

## Règle one-shot

Après un déploiement effectif de la configuration BIND, toute nouvelle tentative de `dnsforge initialize` est bloquée.

Le verrou est écrit dans un fichier technique masqué distinct de `setup.conf` :

```ini
INITIALIZED=true
INITIALIZED_AT=<timestamp UTC>
INITIALIZED_ROLE=<authoritative|proxy>
INITIALIZED_NODE=<node>
```

`setup.conf` reste la source de vérité fonctionnelle du nœud et ne reçoit aucune clé d'état d'initialisation. `dnsforge status` peut afficher l'état d'initialisation en supplément, sans jamais afficher le chemin du fichier de verrou.

Ce verrou interdit ensuite :

```bash
dnsforge initialize
dnsforge initialize --render-only
dnsforge initialize --apply
dnsforge initialize authoritative local
dnsforge initialize proxy local --type forwarder
```

La suppression de ce verrou n'est pas une opération normale. Elle n'est acceptable que dans un scénario contrôlé de reconstruction complète du nœud.

## Sauvegarde avant déploiement

Avant de poser les fichiers DNSForge, la commande déplace les chemins BIND existants dans un répertoire temporaire de sauvegarde, puis produit une archive :

```text
/var/backups/dnsforge/bind-config/<timestamp>.tar.gz
```

Chemins pris en charge :

```text
/etc/named.conf
/etc/named
/etc/bind
/etc/rndc.conf
/etc/rndc.key
/var/named
/var/cache/bind
```

Ce comportement évite les configurations hybrides entre l'ancien BIND et DNSForge.

## Usage direct

```bash
dnsforge initialize authoritative local
```

```bash
dnsforge initialize proxy local --type forwarder
```

```bash
dnsforge initialize proxy local --type hybrid
```

## Usage en deux temps

Rendu uniquement, sans modification système et sans verrou :

```bash
dnsforge initialize authoritative local --render-only
```

Application du rendu existant, avec backup BIND, déploiement et verrouillage :

```bash
dnsforge initialize authoritative local --apply
```

## Dry-run

```bash
dnsforge initialize authoritative local --dry-run
```

Le dry-run affiche le plan, les chemins qui seraient déplacés et l'archive qui serait créée, sans modifier le système et sans poser le verrou d'initialisation.

## Hors périmètre

Les actions suivantes appartiennent à `install/` :

- installation de BIND ;
- installation de `bind-utils` ;
- installation de Keepalived ;
- création des utilisateurs système ;
- création de l'arborescence produit `/opt/dnsforge` et `/etc/dnsforge`.

[Documentation index](./index.md)
