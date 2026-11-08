#!/usr/bin/env bash
set -euo pipefail
verification_dir="$(cd "$(dirname "$0")" && pwd)"
assignment_dir="$(dirname "$verification_dir")"
: "${PROJECT_DIR:?Set PROJECT_DIR to the extracted SharingApp project directory}"
java_dir="$PROJECT_DIR/app/src/main/java/com/example/sharingapp"
gson_jar="$PROJECT_DIR/app/src/include/gson-2.8.2-SNAPSHOT.jar"
classes_dir="$(mktemp -d)"
trap 'rm -rf "$classes_dir"' EXIT
javac -d "$classes_dir" -cp "$gson_jar" "$verification_dir/android/content/Context.java" "$verification_dir/ContactCommandsCheck.java" "$java_dir/Command.java" "$java_dir/Contact.java" "$java_dir/ContactList.java" "$assignment_dir/submission/AddContactCommand.java" "$assignment_dir/submission/EditContactCommand.java" "$assignment_dir/submission/DeleteContactCommand.java"
java -cp "$classes_dir:$gson_jar" com.example.sharingapp.ContactCommandsCheck
