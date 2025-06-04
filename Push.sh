#!/bin/bash
exec &>/dev/null

# Add Text.txt with random number
echo $RANDOM >> Text.txt

# Commit changes with a message
git commit -m "Add Text.txt with random number"

git add .

# git remote add origin https://thephuoc160@github.com/thephuoc160/Git_Push_SSH.git
git remote add origin git@hub1:thephuoc/GitHub_SSH_2.git

git commit -m "$(date +%d-%m-%Y) new add file with random number"

git push -u origin master --force

#!/bin/bash

# Get the current working directory
current_directory=$(pwd)

# Check if the `text.txt` file exists
if [ ! -f "$current_directory/text.txt" ]; then
  echo "The `text.txt` file does not exist."
  exit 1
fi

# Check if the `index.html` file exists
if [ ! -f "$current_directory/index.html" ]; then
  echo "The `index.html` file does not exist."
  exit 1
fi

# Read the contents of the `text.txt` file
text=$(cat "$current_directory/text.txt")

# Đọc từng dòng trong text.txt và thêm \n vào cuối từng dòng
text=$(awk '{printf "%s\\\\n", $0}' "$current_directory/text.txt")

# Ghi đè dòng 168 trong index.html bằng dòng mới
sed -i "168s|.*|const numbersStringFromFileEnd = \"$text\";|" "$current_directory/index.html"

# Save the changes to the `index.html` file
git add "$current_directory/index.html"

# Commit the changes to the `index.html` file
git commit -m "$(date +%d-%m-%Y) Auto-added body of `text.txt` file to `index.html` file."

git push -u origin master --force

