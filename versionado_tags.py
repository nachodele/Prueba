import git
import re

# Ruta al repositorio local
repo_dir = "/home/nachodele/testlab/Prueba"

# Inicializar el repositorio Git
repo = git.Repo(repo_dir)

# Patrón para extraer el número de versión del último tag
version_pattern = re.compile(r"v(\d+\.\d+\.\d+)")

# Determinar el último tag existente y los commits desde ese tag
latest_tag = max(repo.tags, key=lambda t: list(map(int, version_pattern.search(str(t)).group(1).split('.'))) if repo.tags else None)

if latest_tag:
    latest_version = version_pattern.search(str(latest_tag)).group(1)
    major, minor, patch = map(int, latest_version.split('.'))
else:
    major, minor, patch = 0, 0, 0

# Obtener los mensajes de commit desde el último tag
commit_messages = [commit.message.lower() for commit in repo.iter_commits(latest_tag)]

update = False

# Actualizar la versión del siguiente tag según los mensajes de commit
for message in commit_messages:
    if "Breaking:" in message:
        major += 1
        minor = 0
        patch = 0
        break

for message in commit_messages:
    if "New:" in message or "Upgrade:" in message:
        minor += 1
        patch = 0
        break
    else:
        update = True

if update:
    patch += 1

new_tag = f"v{major}.{minor}.{patch}"

try:
    # Crear el nuevo tag
    repo.create_tag(new_tag)

    # Obtener el commit del nuevo tag y los cambios asociados
    tag_commit = list(repo.iter_commits(new_tag))[0]

    # Actualizar el archivo changelog.md con los cambios para el nuevo tag
    with open(f"{repo_dir}/changelog.md", "a") as changelog_file:
        changelog_file.write(f"\n## {new_tag}\n\n{tag_commit.message}\n")

    # Imprimir confirmación del proceso
    print(f"Se ha creado el tag {new_tag} y se ha actualizado changelog.md con los cambios asociados.")
except git.exc.GitCommandError as e:
    print(f"Error al crear el tag: {e}")