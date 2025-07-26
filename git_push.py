#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

# --- Fonctions d'exécution de commandes ---
def _execute_command(command, capture_output=True, check_return=True):
    """
    Exécute une commande shell.
    Retourne (succès_booléen, stdout_string, stderr_string).
    """
    try:
        process = subprocess.run(
            command,
            text=True,
            capture_output=capture_output,
            encoding='utf-8',
            check=check_return # Lève une exception CalledProcessError si le code de retour n'est pas 0
        )
        return True, process.stdout.strip(), process.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip(), e.stderr.strip()
    except FileNotFoundError:
        return False, "", "Commande introuvable. Assurez-vous que le programme est installé et dans votre PATH."

def run_git_command(command_parts, message=None, exit_on_fail=False):
    """
    Exécute une commande Git, affiche son message et gère les succès/échecs.
    """
    full_command = ["git"] + command_parts
    if message:
        print(f"\n--- {message} ---")
    
    success, stdout, stderr = _execute_command(full_command, capture_output=True, check_return=False)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    if not success:
        print(f"Échec de la commande : {' '.join(full_command)}")
        if exit_on_fail:
            sys.exit(1)
    return success, stdout, stderr

def get_git_output(command_parts, exit_on_fail=True):
    """
    Exécute une commande Git et retourne sa sortie standard.
    Quitte le script si la commande échoue et exit_on_fail est True.
    """
    success, stdout, stderr = _execute_command(["git"] + command_parts, capture_output=True, check_return=False)
    if not success:
        print(f"Erreur lors de l'exécution de : {' '.join(['git'] + command_parts)}")
        if stderr:
            print(f"Détails : {stderr}")
        if exit_on_fail:
            sys.exit(1)
    return stdout

# --- Fonctions d'interaction utilisateur ---
def confirm_action(prompt):
    """Demande à l'utilisateur une confirmation (oui/non)."""
    while True:
        choice = input(f"{prompt} [y/N]: ").lower().strip()
        if choice == 'y':
            return True
        elif choice == 'n' or choice == '':
            return False
        else:
            print("Réponse invalide. Veuillez répondre 'y' pour oui ou 'n' pour non.")

# --- Fonctions de vérification et configuration du dépôt ---
def check_git_installed():
    """Vérifie si Git est installé."""
    print("Vérification de l'installation de Git...")
    success, _, _ = _execute_command(["git", "--version"], capture_output=True, check_return=False)
    if success:
        print("Git est installé et détecté.")
        return True
    else:
        print("Erreur : Git n'est pas installé ou n'est pas accessible dans votre PATH.")
        print("Veuillez installer Git pour continuer.")
        return False

def get_current_branch():
    """Retourne le nom de la branche actuelle."""
    return get_git_output(["rev-parse", "--abbrev-ref", "HEAD"])

def setup_remote_origin():
    """
    Configure ou vérifie le dépôt distant 'origin'.
    Demande à l'utilisateur l'URL si nécessaire.
    """
    print("\n--- Configuration du dépôt distant 'origin' ---")
    
    # Tente de récupérer l'URL existante de 'origin'
    existing_url = get_git_output(["config", "--get", "remote.origin.url"], exit_on_fail=False)

    if existing_url:
        print(f"Le dépôt distant 'origin' est configuré avec l'URL : {existing_url}")
        if not confirm_action("Est-ce l'URL correcte pour votre dépôt ?"):
            new_url = input("Veuillez entrer l'URL correcte de votre dépôt GitHub : ").strip()
            if not new_url:
                print("URL vide. Annulation de la mise à jour du dépôt distant.")
                return False
            success, _, _ = run_git_command(["remote", "set-url", "origin", new_url], message=f"Mise à jour de l'URL de 'origin' vers {new_url}")
            if not success:
                print("Échec de la mise à jour de l'URL du dépôt distant.")
                return False
            print("URL du dépôt distant mise à jour avec succès.")
    else:
        print("Le dépôt distant 'origin' n'est pas configuré.")
        repo_url = input("Veuillez entrer l'URL de votre dépôt GitHub (ex: https://github.com/utilisateur/repo.git) : ").strip()
        if not repo_url:
            print("URL vide. Annulation de l'ajout du dépôt distant.")
            return False
        success, _, _ = run_git_command(["remote", "add", "origin", repo_url], message=f"Ajout du dépôt distant 'origin' avec l'URL {repo_url}")
        if not success:
            print("Échec de l'ajout du dépôt distant.")
            return False
        print("Dépôt distant 'origin' ajouté avec succès.")
    return True

def has_pending_changes():
    """Vérifie s'il y a des modifications stagées, non stagées ou non suivies."""
    status_output = get_git_output(["status", "--porcelain"], exit_on_fail=False)
    return bool(status_output.strip())

# --- Fonction principale ---
def main():
    """Fonction principale orchestrant le processus Git automatisé."""

    if not check_git_installed():
        sys.exit(1)

    if not os.path.isdir(".git"):
        print("Erreur : Ce script doit être exécuté à la racine d'un dépôt Git.")
        sys.exit(1)

    print("\n--- Démarrage du processus Git automatisé ---")

    # 1. Configuration du dépôt distant
    if not setup_remote_origin():
        print("Impossible de configurer le dépôt distant. Abandon.")
        sys.exit(1)

    # 2. Vérification et indexation des fichiers
    print("\n--- Vérification des modifications et indexation ---")
    if not has_pending_changes():
        print("Aucune modification détectée dans le répertoire de travail. Rien à commiter.")
        sys.exit(0)
    
    print("Des modifications ont été détectées. Indexation de tous les fichiers (`git add .`).")
    success, _, _ = run_git_command(["add", "."], exit_on_fail=True)
    if not success:
        print("Échec de l'indexation des fichiers. Abandon.")
        sys.exit(1)
    print("Fichiers indexés avec succès.")

    # 3. Récupération des dernières modifications (Pull --rebase)
    print("\n--- Synchronisation avec le dépôt distant (`git pull --rebase`) ---")
    current_branch = get_current_branch()
    success, stdout, stderr = run_git_command(["pull", "--rebase", "origin", current_branch])

    if not success:
        if "conflict" in stderr or "conflict" in stdout:
            print("Conflit de fusion détecté. Veuillez résoudre les conflits manuellement, puis exécutez `git rebase --continue` et relancez ce script.")
            print("Utilisez `git status` pour voir les fichiers en conflit.")
            sys.exit(1)
        else:
            print("Échec du pull --rebase. Cela peut indiquer un problème de connexion ou de permissions.")
            if not confirm_action("Voulez-vous quand même tenter le commit et le push ? (Risque de conflit si des modifications distantes existent)"):
                print("Pull --rebase échoué et push annulé. Abandon.")
                sys.exit(1)
    else:
        print("Synchronisation effectuée avec succès.")

    # 4. Création du commit
    print("\n--- Création du commit ---")
    commit_message = input("Entrez votre message de commit (ex: 'feat: Ajout fonctionnalité X') : ").strip()
    if not commit_message:
        commit_message = f"chore: Mise à jour automatique"
        print(f"Message de commit par défaut utilisé : '{commit_message}'")
    
    success, _, stderr = run_git_command(["commit", "-m", commit_message])
    if not success:
        if "nothing to commit" in stderr or "no changes added to commit" in stderr:
            print("Aucune modification à commiter. Le répertoire de travail est propre.")
        else:
            print("Échec du commit. Veuillez vérifier les messages d'erreur ci-dessus.")
        sys.exit(1)
    print("Commit créé avec succès.")

    # 5. Push vers GitHub
    print("\n--- Push vers GitHub ---")
    current_branch = get_current_branch() # Récupère la branche à nouveau au cas où elle aurait changé
    
    success, _, stderr = run_git_command(["push", "origin", current_branch])
    
    if success:
        print("\nPush réussi ! Toutes les modifications sont sur GitHub.")
        print(f"Vous pouvez consulter votre dépôt ici : {get_git_output(['config', '--get', 'remote.origin.url'], exit_on_fail=False).replace('.git', '')}/tree/{current_branch}")
        return

    # Gestion des échecs de push courants
    if "has no upstream branch" in stderr:
        print(f"La branche distante '{current_branch}' n'existe pas ou n'est pas configurée pour le suivi.")
        if confirm_action(f"Voulez-vous configurer la branche amont et pousser (`git push --set-upstream origin {current_branch}`) ?"):
            success, _, _ = run_git_command(["push", "--set-upstream", "origin", current_branch])
            if success:
                print(f"\nSuccès ! La branche distante a été créée et est maintenant suivie.")
                print(f"Vous pouvez consulter votre dépôt ici : {get_git_output(['config', '--get', 'remote.origin.url'], exit_on_fail=False).replace('.git', '')}/tree/{current_branch}")
            else:
                print(f"\nLe push a échoué à nouveau. Veuillez vérifier vos permissions du dépôt.")
        else:
            print("Configuration de la branche amont annulée. Le push n'a pas été effectué.")
    elif "authentication failed" in stderr or "support for password authentication was removed" in stderr:
        print("\nLe push a échoué : Erreur d'authentification.")
        print("GitHub a retiré le support de l'authentification par mot de passe pour les opérations Git.")
        print("Veuillez vérifier vos identifiants (jeton d'accès personnel - PAT, ou clé SSH).")
        print("Pour générer un PAT : https://docs.github.com/fr/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens")
    elif "push declined" in stderr or "protected branch" in stderr:
        print("\nLe push a échoué : Push refusé ou restrictions de branche protégée.")
        print(f"Vous n'avez peut-être pas la permission de pousser directement sur '{current_branch}'.")
        print("Considérez la création d'une Pull Request ou poussez vers une branche différente.")
    elif "non-fast-forward" in stderr:
        print("\nLe push a échoué : Des modifications distantes existent que vous n'avez pas.")
        print("Cela signifie que le dépôt distant a été mis à jour depuis votre dernier pull.")
        print("Veuillez exécuter `git pull --rebase` à nouveau pour synchroniser vos modifications, puis relancez ce script.")
    else:
        print("\nLe push a échoué : Une erreur inattendue s'est produite.")
        print("Détails de l'erreur :")
        print(stderr)

# Point d'entrée du script
if __name__ == "__main__":
    main()
