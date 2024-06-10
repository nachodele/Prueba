import git
import re

repo_dir = "/home/nachodele/testlab/Prueba"
repo = git.Repo(repo_dir)
version_pattern = re.compile(r"v(\d+\.\d+\.\d+)")

# Definir una función para comparar versiones según las reglas de Semantic Versioning
def compare_versions(v1, v2):
    v1_parts = list(map(int, v1.split('.')))
    v2_parts = list(map(int, v2.split('.')))
    
    for part1, part2 in zip(v1_parts, v2_parts):
        if part1 < part2:
            return -1
        if part1 > part2:
            return 1
    
    return 0

# Determinar la nueva versión del siguiente tag según los mensajes de commit
def calculate_next_version(current_version, commit_messages):
    major, minor, patch = map(int, current_version.split('.'))
    
    breaking_change = False
    for message in commit_messages:
        message_lower = message.lower()
        
        if "breaking" in message_lower:
            breaking_change = True
            break
        elif "new" in message_lower or "upgrade" in message_lower:
            if major == 0:
                major += 1
                minor = 0
                patch = 0
            else:
                minor += 1
                patch = 0
            break
    
    if breaking_change:
        major += 1
        minor = 0
        patch = 0
    else:
        patch += 1
    
    return f"{major}.{minor}.{patch}"

# Determinar el último tag existente
latest_tag = max(repo.tags, key=lambda t: list(map(int, version_pattern.search(str(t)).group(1).split('.'))) if repo.tags else None)

if latest_tag:
    latest_version = version_pattern.search(str(latest_tag)).group(1)
else:
    latest_version = "0.0.0"

# Obtener los mensajes de commit desde el último tag
commit_messages = [commit.message.lower() for commit in repo.iter_commits(latest_tag)]

# Calcular la nueva versión del siguiente tag
new_version = calculate_next_version(latest_version, commit_messages)

# Crear el nuevo tag con la nueva versión
new_tag = f"v{new_version}"

try:
    # Crear el nuevo tag y actualizar changelog.md
    repo.create_tag(new_tag)
    tag_commit = list(repo.iter_commits(new_tag))[0]

    with open(f"{repo_dir}/changelog.md", "a") as changelog_file:
        changelog_file.write(f"\n## {new_tag}\n\n{tag_commit.message}\n")

    print(f"Se ha creado el tag {new_tag} y se ha actualizado changelog.md con los cambios asociados.")
except git.exc.GitCommandError as e:
    print(f"Error al crear el tag: {e}")