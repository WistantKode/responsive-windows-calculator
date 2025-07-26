#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour déconnecter un projet de GitHub et supprimer le contrôle de version local.
ATTENTION : Cette action est irréversible et supprime tout l'historique des commits.
"""

import os
import shutil
import subprocess
import sys

# La phrase exacte que l'utilisateur doit taper pour valider la suppression.
CONFIRMATION_PHRASE = "oui, je supprime git"

def execute_command(command):
    """Exécute une commande shell et retourne True si elle réussit."""
    try:
        # Nous n'affichons la sortie que s'il y a une erreur pour garder le script propre.
        subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        return True
    except FileNotFoundError:
        print("Erreur : La commande 'git' est introuvable. Assurez-vous que Git est installé.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        # L'échec n'est pas critique (ex: le remote n'existe déjà plus).
        return False

def unlink_project():
    """
    Fonction principale qui guide l'utilisateur pour déconnecter le projet de Git.
    """
    project_path = os.getcwd()
    git_dir_path = os.path.join(project_path, '.git')

    print("--- Script de suppression du contrôle de version Git ---")
    print(f"Dossier de travail actuel : {project_path}")

    # 1. Vérifier si le dossier est un dépôt Git.
    if not os.path.isdir(git_dir_path):
        print("\nInformation : Aucun dépôt Git (`.git`) n'a été trouvé ici.")
        print("Le projet n'est pas sous contrôle de version. Aucune action n'est requise.")
        return

    # 2. Afficher un avertissement très clair.
    print("\n" + "="*60)
    print("ATTENTION : ACTION DESTRUCTIVE ET IRRÉVERSIBLE")
    print("="*60)
    print("Vous êtes sur le point de :")
    print("  1. Supprimer la connexion de ce projet à son dépôt distant sur GitHub.")
    print("  2. Supprimer DÉFINITIVEMENT tout l'historique des versions (les commits).")
    print("\nVos fichiers de code actuels ne seront PAS touchés, mais l'historique sera perdu.")
    print("="*60)

    # 3. Demander une confirmation explicite.
    try:
        user_input = input(f"\nPour confirmer, tapez la phrase exacte suivante : '{CONFIRMATION_PHRASE}'\n> ")
    except (KeyboardInterrupt, EOFError):
        print("\n\nOpération annulée par l'utilisateur.")
        sys.exit(1)

    if user_input.strip() != CONFIRMATION_PHRASE:
        print("\nConfirmation incorrecte. Opération annulée. Aucune modification n'a été faite.")
        return

    print("\nConfirmation reçue. Lancement de la procédure...")

    # 4. Supprimer le lien distant.
    print("\nÉtape 1/2 : Suppression du lien vers le dépôt distant ('origin')...")
    if execute_command(["git", "remote", "remove", "origin"]):
        print(" -> Lien distant 'origin' supprimé avec succès.")
    else:
        print(" -> Lien distant 'origin' non trouvé ou déjà supprimé.")

    # 5. Supprimer le dossier .git.
    print("\nÉtape 2/2 : Suppression du dossier de contrôle de version local (.git)...")
    try:
        shutil.rmtree(git_dir_path)
        print(f" -> Le dossier '.git' a été supprimé avec succès.")
    except OSError as e:
        print(f"\nERREUR CRITIQUE : Impossible de supprimer le dossier '.git'.\nErreur : {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "-"*60 + "\nOpération terminée.\nCe projet n'est plus sous contrôle de version Git.\n" + "-"*60)

if __name__ == "__main__":
    unlink_project()