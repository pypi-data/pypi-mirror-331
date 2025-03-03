import os

def create_project_structure(project_name, base_path=None):
    # Set default base path to current working directory if not provided
    if base_path is None:
        base_path = os.getcwd()
    
    # Combine base path and project name to determine the project directory
    project_path = os.path.join(base_path, project_name)
    
    # Define folder and file structure
    directories = [
        os.path.join(project_path, 'css'),
        os.path.join(project_path, 'js')
    ]
    
    files = [
        os.path.join(project_path, 'index.html'),
        os.path.join(project_path, 'css', 'style.css'),
        os.path.join(project_path, 'js', 'script.js')
    ]
    
    # Create the directories
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Create the HTML file with linked CSS and JS
    with open(files[0], 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Project</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Welcome to the Simple Project</h1>
    <script src="js/script.js"></script>
</body>
</html>""")
    
    # Create empty CSS file
    with open(files[1], 'w') as f:
        f.write("")  # Empty content for style.css
    
    # Create empty JS file
    with open(files[2], 'w') as f:
        f.write("")  # Empty content for script.js
    
    print(f"Project '{project_name}' structure created successfully at '{project_path}'!")

# Usage: Call the function with your desired project name and optional base path
if __name__ == "__main__":
    project_name = input("Enter project name: ")
    base_path = input("Enter base path for the project (leave empty for current directory): ").strip()
    
    if base_path == "":
        base_path = None  # Use default behavior for current working directory
    
    create_project_structure(project_name, base_path)