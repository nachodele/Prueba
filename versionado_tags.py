import git
import re

# Ruta al repositorio local
repo_dir = "/home/nachodele/testlab/Prueba"

# Inicializar el repositorio Git
repo = git.Repo(repo_dir)

# Patrón para extraer el número de versión del último tag
version_pattern = re.compile(r"v(\d+\.\d+\.\d+)")

# Determinar la última versión y definir la próxima versión

latest_tag = max(repo.tags, key=lambda t: list(map(int, version_pattern.search(str(t)).group(1).split('.'))) if repo.tags else None)
tag_versions = {"major": 0, "minor": 0, "patch": 0}

# Obtener los mensajes de commit para actualizar las versiones
commit_messages = [commit.message.lower() for commit in repo.iter_commits(latest_tag)]

for message in commit_messages:
    first_word = message.split()[0]

    if first_word == "breaking":
        tag_versions["major"] += 1
        tag_versions["minor"] = 0
        tag_versions["patch"] = 0
    elif first_word == "new" or first_word == "upgrade":
        tag_versions["minor"] += 1
        tag_versions["patch"] = 0
    else:
        tag_versions["patch"] += 1

new_tag = f"v{tag_versions['major']}.{tag_versions['minor']}.{tag_versions['patch']}"

# Crear el nuevo tag
repo.create_tag(new_tag)

# Obtener los mensajes de commit y los cambios asociados a este tag
tag_commit = list(repo.iter_commits(new_tag))[0]

# Actualizar el archivo changelog.md
with open(f"{repo_dir}/changelog.md", "a") as changelog_file:
    changelog_file.write(f"\n## {new_tag}\n\n{tag_commit.message}\n")

print(f"Se ha creado el tag {new_tag} y se ha actualizado changelog.md con los cambios asociados.")